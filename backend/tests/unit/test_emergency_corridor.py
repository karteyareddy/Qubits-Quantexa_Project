"""Unit tests for Stage 13 Emergency Green Corridor subsystem."""

import pytest
from app.adaptive.controller import AdaptiveSignalPolicy
from app.domain.signal import SignalPhase
from app.domain.vehicle import EmergencySubtype, Vehicle, VehicleState, VehicleType
from app.emergency.controller import EmergencyCorridorController
from app.emergency.corridor import EmergencyCorridorPlanner
from app.emergency.models import CorridorStatus, EmergencyCorridorConfig
from app.emergency.predictor import EmergencyETAPredictor
from app.emergency.route import EmergencyRouteError, EmergencyRouteExtractor
from app.emergency.service import EmergencyCorridorService
from app.routing.demo_network import build_demo_network
from app.routing.routes import generate_candidate_routes
from app.signals.policy import SignalSystem
from app.simulation.engine import TrafficSimulation
from app.simulation.scenarios import low_traffic_scenario


def test_emergency_route_extractor() -> None:
    network = build_demo_network()
    em_veh = Vehicle(
        vehicle_id="amb_01",
        vehicle_type=VehicleType.EMERGENCY,
        is_emergency=True,
        emergency_subtype=EmergencySubtype.AMBULANCE,
        origin="I1",
        destination="I6",
    )

    route = EmergencyRouteExtractor.extract_and_validate_route(em_veh, network)
    assert route.node_ids[0] == "I1"
    assert route.node_ids[-1] == "I6"

    sequence = EmergencyRouteExtractor.extract_intersection_sequence(network, route)
    assert len(sequence) >= 1
    # Check direction preserving sequence
    for inter_id, in_e, out_e in sequence:
        assert inter_id in ("I1", "I2", "I3", "I4", "I5", "I6")
        assert in_e != ""
        assert out_e != ""

    reg_veh = Vehicle(
        vehicle_id="reg_01",
        vehicle_type=VehicleType.REGULAR,
        is_emergency=False,
        origin="I1",
        destination="I6",
    )
    with pytest.raises(EmergencyRouteError):
        EmergencyRouteExtractor.extract_and_validate_route(reg_veh, network)


def test_eta_prediction_and_phase_mapping() -> None:
    network = build_demo_network()
    em_veh = Vehicle(
        vehicle_id="amb_01",
        vehicle_type=VehicleType.EMERGENCY,
        is_emergency=True,
        emergency_subtype=EmergencySubtype.AMBULANCE,
        origin="I1",
        destination="I6",
    )
    route = EmergencyRouteExtractor.extract_and_validate_route(em_veh, network)
    em_veh = em_veh.model_copy(update={"route": route})
    sequence = EmergencyRouteExtractor.extract_intersection_sequence(network, route)

    cfg = EmergencyCorridorConfig(arrival_buffer_seconds=3.0, clearance_buffer_seconds=4.0)
    reservations = EmergencyETAPredictor.predict_corridor_reservations(
        vehicle=em_veh,
        network=network,
        sequence=sequence,
        current_time=10.0,
        config=cfg,
    )

    assert len(reservations) == len(sequence)
    prev_eta = 0.0
    for res in reservations:
        assert res.arrival_time_seconds >= 10.0
        assert res.arrival_time_seconds >= prev_eta
        assert res.green_window_start <= res.arrival_time_seconds
        assert res.green_window_end >= res.arrival_time_seconds
        assert res.required_phase in (SignalPhase.NS_GREEN, SignalPhase.EW_GREEN)
        prev_eta = res.arrival_time_seconds


def test_corridor_planner() -> None:
    network = build_demo_network()
    em_veh = Vehicle(
        vehicle_id="amb_01",
        vehicle_type=VehicleType.EMERGENCY,
        is_emergency=True,
        emergency_subtype=EmergencySubtype.AMBULANCE,
        origin="I1",
        destination="I6",
    )

    corridor = EmergencyCorridorPlanner.plan_corridor(
        vehicle=em_veh,
        network=network,
        current_time=0.0,
    )

    assert corridor.status == CorridorStatus.PLANNED
    assert corridor.vehicle_id == "amb_01"
    assert len(corridor.intersections) > 0


def test_controller_preemption_and_overrides() -> None:
    network = build_demo_network()
    system = SignalSystem.for_network(network)
    policy = AdaptiveSignalPolicy(signal_system=system, network=network)

    em_veh = Vehicle(
        vehicle_id="amb_01",
        vehicle_type=VehicleType.EMERGENCY,
        is_emergency=True,
        emergency_subtype=EmergencySubtype.AMBULANCE,
        origin="I1",
        destination="I6",
    )
    corridor = EmergencyCorridorPlanner.plan_corridor(em_veh, network, current_time=10.0)
    corridor = corridor.model_copy(
        update={"status": CorridorStatus.ACTIVE, "activated_at_seconds": 10.0}
    )

    target_res = corridor.intersections[0]
    mid_time = (target_res.green_window_start + target_res.green_window_end) / 2.0

    phase_override = EmergencyCorridorController.get_intersection_override(
        corridor, target_res.intersection_id, mid_time
    )
    assert phase_override == target_res.required_phase

    # Outside window returns None
    assert (
        EmergencyCorridorController.get_intersection_override(
            corridor, target_res.intersection_id, target_res.green_window_end + 10.0
        )
        is None
    )

    overrides = EmergencyCorridorController.apply_corridor_overrides(
        [corridor], system, policy, mid_time
    )
    assert target_res.intersection_id in overrides
    assert policy.states_at(mid_time) is not None


def test_emergency_corridor_service_lifecycle() -> None:
    scenario = low_traffic_scenario()
    sim = TrafficSimulation(scenario)
    system = SignalSystem.for_network(scenario.network)
    policy = AdaptiveSignalPolicy(signal_system=system, network=scenario.network)

    service = EmergencyCorridorService()

    routes = generate_candidate_routes(scenario.network, "I1", "I6")
    # Inject emergency vehicle at t=5.0
    em_veh = Vehicle(
        vehicle_id="amb_test",
        vehicle_type=VehicleType.EMERGENCY,
        is_emergency=True,
        emergency_subtype=EmergencySubtype.AMBULANCE,
        origin="I1",
        destination="I6",
        route=routes[0],
        candidate_routes=routes,
        arrival_time_seconds=5.0,
        state=VehicleState.PENDING,
    )
    sim._state = sim.state.model_copy(
        update={"pending_vehicles": sim.state.pending_vehicles + (em_veh,)}
    )

    # Advance sim to t=5.0
    sim.step(5.0)

    # Service update should discover emergency vehicle and activate corridor
    active = service.update(sim, signal_system=system, adaptive_policy=policy)
    assert len(active) == 1
    corridor = active[0]
    assert corridor.status == CorridorStatus.ACTIVE
    assert corridor.vehicle_id == "amb_test"

    # Mark vehicle completed -> Corridor releases
    completed_veh = em_veh.model_copy(
        update={"state": VehicleState.ARRIVED, "completion_time_seconds": 25.0}
    )
    sim._state = sim.state.model_copy(
        update={"completed_vehicles": sim.state.completed_vehicles + (completed_veh,)}
    )

    active_after = service.update(sim, signal_system=system, adaptive_policy=policy)
    assert len(active_after) == 0

    history = service.corridor_history
    assert len(history) == 1
    assert history[0].status == CorridorStatus.COMPLETED
