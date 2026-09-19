"""Behavior tests for deterministic vehicle movement and queues."""

import pytest
from app.core.errors import SimulationError
from app.domain.network import Network, NetworkEdge, NetworkNode
from app.domain.route import Route
from app.domain.vehicle import EmergencySubtype, Vehicle, VehicleState, VehicleType
from app.simulation.engine import TrafficSimulation
from app.simulation.models import ScheduledArrival, SimulationConfiguration, SimulationScenario


def test_step_rejects_non_positive_interval() -> None:
    simulation = TrafficSimulation(_single_edge_scenario())

    with pytest.raises(SimulationError, match="positive"):
        simulation.step(0.0)


def test_vehicle_spawns_at_scheduled_time() -> None:
    simulation = TrafficSimulation(_single_edge_scenario(arrival_time=2.0))

    simulation.step()
    state = simulation.step()

    assert state.simulation_time_seconds == 2.0
    assert state.counts.active == 1
    assert state.active_vehicles[0].position_on_edge == 0.0


def test_vehicle_moves_along_an_edge_without_waiting() -> None:
    simulation = TrafficSimulation(_single_edge_scenario(length_m=100.0))

    state = simulation.step()
    vehicle = state.active_vehicles[0]

    assert vehicle.position_on_edge == 0.1
    assert vehicle.distance_travelled_m == 10.0
    assert vehicle.waiting_time_seconds == 0.0


def test_vehicle_transitions_to_next_route_edge() -> None:
    simulation = TrafficSimulation(_two_edge_scenario(length_m=5.0))

    state = simulation.step(0.75)
    vehicle = state.active_vehicles[0]

    assert vehicle.current_edge_id == "I2->I3"
    assert vehicle.current_route_index == 1
    assert vehicle.position_on_edge == 0.5


def test_vehicle_completes_and_exits_network() -> None:
    simulation = TrafficSimulation(_single_edge_scenario(length_m=10.0))

    state = simulation.step()
    vehicle = state.completed_vehicles[0]

    assert state.counts.completed == 1
    assert state.edge_occupancy["I1->I2"] == ()
    assert vehicle.state is VehicleState.ARRIVED
    assert vehicle.completion_time_seconds == 1.0


def test_full_edge_forms_queue_and_accumulates_only_waiting_time() -> None:
    scenario = _single_edge_scenario(length_m=100.0, capacity=1.0, vehicle_count=2)
    simulation = TrafficSimulation(scenario)

    assert simulation.state.counts.waiting == 1
    assert simulation.state.edge_queues["I1->I2"] == ("vehicle-002",)

    state = simulation.step()
    vehicles = {vehicle.vehicle_id: vehicle for vehicle in state.active_vehicles}

    assert vehicles["vehicle-001"].waiting_time_seconds == 0.0
    assert vehicles["vehicle-002"].waiting_time_seconds == 1.0
    assert state.intersection_approach_queues["origin:I1"] == ("vehicle-002",)


def test_full_next_edge_blocks_intersection_transition() -> None:
    simulation = TrafficSimulation(_blocked_transition_scenario())

    state = simulation.step()
    mover = next(
        vehicle for vehicle in state.active_vehicles if vehicle.vehicle_id == "mover"
    )

    assert mover.state is VehicleState.WAITING
    assert mover.current_edge_id == "I1->I2"
    assert mover.position_on_edge == 1.0
    assert mover.waiting_time_seconds == 0.5
    assert state.edge_queues["I2->I3"] == ("mover",)
    assert state.intersection_approach_queues["I1->I2"] == ("mover",)


def test_emergency_identity_survives_simulation_steps() -> None:
    scenario = _single_edge_scenario(emergency=True)
    simulation = TrafficSimulation(scenario)

    vehicle = simulation.step().active_vehicles[0]

    assert vehicle.is_emergency is True
    assert vehicle.emergency_subtype is EmergencySubtype.AMBULANCE
    assert vehicle.priority_weight == 10


def test_state_is_json_serializable() -> None:
    state = TrafficSimulation(_single_edge_scenario()).step()

    payload = state.model_dump(mode="json")

    assert payload["counts"]["active"] == 1
    assert payload["edge_occupancy"]["I1->I2"] == ["vehicle-001"]


def _single_edge_scenario(
    *,
    length_m: float = 100.0,
    capacity: float = 2.0,
    arrival_time: float = 0.0,
    vehicle_count: int = 1,
    emergency: bool = False,
) -> SimulationScenario:
    network = Network(
        network_id="single-edge",
        directed=True,
        nodes=(NetworkNode(node_id="I1"), NetworkNode(node_id="I2")),
        edges=(
            NetworkEdge(
                edge_id="I1->I2",
                source="I1",
                target="I2",
                length_m=length_m,
                capacity=capacity,
                free_flow_speed_kph=36.0,
                travel_time_seconds=length_m / 10.0,
            ),
        ),
    )
    route = Route(
        route_id="single-route",
        node_ids=("I1", "I2"),
        edge_ids=("I1->I2",),
        estimated_travel_time_seconds=length_m / 10.0,
        distance_m=length_m,
    )
    arrivals = tuple(
        ScheduledArrival(
            arrival_time_seconds=arrival_time,
            vehicle=Vehicle(
                vehicle_id=f"vehicle-{index + 1:03d}",
                vehicle_type=(VehicleType.EMERGENCY if emergency else VehicleType.REGULAR),
                origin="I1",
                destination="I2",
                route=route,
                arrival_time_seconds=arrival_time,
                is_emergency=emergency,
                emergency_subtype=(EmergencySubtype.AMBULANCE if emergency else None),
                priority_weight=10 if emergency else 1,
            ),
        )
        for index in range(vehicle_count)
    )
    return SimulationScenario(
        scenario_id="single-edge-scenario",
        seed=42,
        duration_seconds=60.0,
        network=network,
        arrivals=arrivals,
        configuration=SimulationConfiguration(timestep_seconds=1.0),
    )


def _two_edge_scenario(*, length_m: float) -> SimulationScenario:
    network = Network(
        network_id="two-edge",
        directed=True,
        nodes=tuple(NetworkNode(node_id=node_id) for node_id in ("I1", "I2", "I3")),
        edges=tuple(
            NetworkEdge(
                edge_id=edge_id,
                source=source,
                target=target,
                length_m=length_m,
                capacity=2.0,
                free_flow_speed_kph=36.0,
                travel_time_seconds=length_m / 10.0,
            )
            for edge_id, source, target in (
                ("I1->I2", "I1", "I2"),
                ("I2->I3", "I2", "I3"),
            )
        ),
    )
    route = Route(
        route_id="two-edge-route",
        node_ids=("I1", "I2", "I3"),
        edge_ids=("I1->I2", "I2->I3"),
        estimated_travel_time_seconds=length_m / 5.0,
        distance_m=length_m * 2,
    )
    arrival = ScheduledArrival(
        arrival_time_seconds=0.0,
        vehicle=Vehicle(
            vehicle_id="vehicle-001",
            vehicle_type=VehicleType.REGULAR,
            origin="I1",
            destination="I3",
            route=route,
        ),
    )
    return SimulationScenario(
        scenario_id="two-edge-scenario",
        seed=42,
        duration_seconds=60.0,
        network=network,
        arrivals=(arrival,),
    )


def _blocked_transition_scenario() -> SimulationScenario:
    network = Network(
        network_id="blocked-transition",
        directed=True,
        nodes=tuple(NetworkNode(node_id=node_id) for node_id in ("I1", "I2", "I3")),
        edges=(
            NetworkEdge(
                edge_id="I1->I2",
                source="I1",
                target="I2",
                length_m=5.0,
                capacity=2.0,
                free_flow_speed_kph=36.0,
                travel_time_seconds=0.5,
            ),
            NetworkEdge(
                edge_id="I2->I3",
                source="I2",
                target="I3",
                length_m=100.0,
                capacity=1.0,
                free_flow_speed_kph=36.0,
                travel_time_seconds=10.0,
            ),
        ),
    )
    blocker_route = Route(
        route_id="blocker-route",
        node_ids=("I2", "I3"),
        edge_ids=("I2->I3",),
        estimated_travel_time_seconds=10.0,
        distance_m=100.0,
    )
    mover_route = Route(
        route_id="mover-route",
        node_ids=("I1", "I2", "I3"),
        edge_ids=("I1->I2", "I2->I3"),
        estimated_travel_time_seconds=10.5,
        distance_m=105.0,
    )
    arrivals = tuple(
        ScheduledArrival(arrival_time_seconds=0.0, vehicle=vehicle)
        for vehicle in (
            Vehicle(
                vehicle_id="blocker",
                vehicle_type=VehicleType.REGULAR,
                origin="I2",
                destination="I3",
                route=blocker_route,
            ),
            Vehicle(
                vehicle_id="mover",
                vehicle_type=VehicleType.REGULAR,
                origin="I1",
                destination="I3",
                route=mover_route,
            ),
        )
    )
    return SimulationScenario(
        scenario_id="blocked-transition-scenario",
        seed=42,
        duration_seconds=60.0,
        network=network,
        arrivals=arrivals,
    )
