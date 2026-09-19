"""Unit tests for SignalQuboBuilder, penalty expansion, and hand-checkable example."""

from app.domain.network import Network, NetworkEdge, NetworkNode
from app.domain.vehicle import EmergencySubtype, Vehicle, VehicleState, VehicleType
from app.signals.qubo.builder import SignalQuboBuilder
from app.signals.qubo.config import SignalQuboConfig
from app.simulation.models import SimulationCounts, SimulationState


def test_hand_checkable_1_intersection_2_phase_qubo_expansion() -> None:
    """Hand-checkable test verifying A*(x0 + x1 - 1)^2 = A(-x0 - x1 + 2*x0*x1) + A."""
    network = Network(
        network_id="test-net",
        directed=True,
        nodes=(
            NetworkNode(node_id="I1", is_intersection=True, x=0.0, y=0.0),
            NetworkNode(node_id="I2", is_intersection=False, x=100.0, y=0.0),
        ),
        edges=(
            NetworkEdge(
                edge_id="E1",
                source="I2",
                target="I1",
                length_m=100.0,
                capacity=10.0,
                free_flow_speed_kph=40.0,
                travel_time_seconds=9.0,
            ),
        ),
    )
    state = SimulationState(
        simulation_time_seconds=0.0,
        counts=SimulationCounts(pending=0, active=0, completed=0, waiting=0, throughput=0),
    )

    config = SignalQuboConfig(
        horizon_intervals=1,
        constraint_penalty=100.0,
        queue_weight=0.0,
        waiting_weight=0.0,
        throughput_weight=0.0,
        emergency_weight=0.0,
        switch_weight=0.0,
    )

    builder = SignalQuboBuilder(config=config)
    Q, offset, var_names, _var_map = builder.build_qubo(network, state)

    assert len(var_names) == 2  # x_I1_P0_T0, x_I1_P1_T0
    x0, x1 = var_names[0], var_names[1]

    assert Q[(x0, x0)] == -100.0
    assert Q[(x1, x1)] == -100.0
    pair = (min(x0, x1), max(x0, x1))
    assert Q[pair] == 200.0
    assert offset == 100.0


def test_emergency_weighting_increases_unserved_emergency_cost() -> None:
    network = Network(
        network_id="test-net",
        directed=True,
        nodes=(
            NetworkNode(node_id="I1", is_intersection=True, x=0.0, y=0.0),
            NetworkNode(node_id="N1", is_intersection=False, x=0.0, y=100.0),
        ),
        edges=(
            NetworkEdge(
                edge_id="E_NS",
                source="N1",
                target="I1",
                length_m=100.0,
                capacity=10.0,
                free_flow_speed_kph=40.0,
                travel_time_seconds=9.0,
            ),
        ),
    )

    em_vehicle = Vehicle(
        vehicle_id="em1",
        vehicle_type=VehicleType.EMERGENCY,
        origin="N1",
        destination="I1",
        is_emergency=True,
        emergency_subtype=EmergencySubtype.AMBULANCE,
        state=VehicleState.WAITING,
        waiting_time_seconds=10.0,
    )

    reg_vehicle = Vehicle(
        vehicle_id="reg1",
        vehicle_type=VehicleType.REGULAR,
        origin="N1",
        destination="I1",
        is_emergency=False,
        state=VehicleState.WAITING,
        waiting_time_seconds=10.0,
    )

    state_normal = SimulationState(
        simulation_time_seconds=10.0,
        active_vehicles=(reg_vehicle,),
        edge_queues={"E_NS": ("reg1",)},
        counts=SimulationCounts(pending=0, active=1, completed=0, waiting=1, throughput=0),
    )

    state_emergency = SimulationState(
        simulation_time_seconds=10.0,
        active_vehicles=(em_vehicle,),
        edge_queues={"E_NS": ("em1",)},
        counts=SimulationCounts(pending=0, active=1, completed=0, waiting=1, throughput=0),
    )

    cfg = SignalQuboConfig(
        horizon_intervals=1,
        constraint_penalty=100.0,
        queue_weight=2.0,
        waiting_weight=0.0,
        emergency_weight=20.0,
    )

    b = SignalQuboBuilder(cfg)
    Q_norm, _off_n, _v_n, _m_n = b.build_qubo(network, state_normal)
    Q_em, _off_e, _v_e, _m_e = b.build_qubo(network, state_emergency)

    # In EW_GREEN (P0), NS_GREEN (P1) is unserved
    # Emergency state should have much higher penalty on P0 (EW_GREEN)
    var_ew = "x_I1_P0_T0"
    assert Q_em[(var_ew, var_ew)] > Q_norm[(var_ew, var_ew)]
