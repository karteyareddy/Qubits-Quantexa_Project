"""Unit tests for Stage 17 Hardening & Reliability."""

import pytest
from app.domain.network import Network, NetworkEdge, NetworkNode
from app.events.models import CongestionSpikeEvent
from app.hardening import (
    PlatformResourceLimits,
    ValidationError,
    compute_state_trajectory_hash,
    validate_event_payload,
    validate_network_edge_exists,
    validate_network_node_exists,
    verify_simulation_equivalence,
)
from app.optimization.hybrid_solver import HybridOptimizerConfig, HybridSignalOptimizer
from app.simulation.engine import TrafficSimulation
from app.simulation.scenarios import low_traffic_scenario


def test_resource_limits_validation() -> None:
    limits = PlatformResourceLimits()

    assert limits.validate_simulation_duration(100.0) == 100.0

    with pytest.raises(ValueError, match="strictly positive"):
        limits.validate_simulation_duration(-5.0)

    with pytest.raises(ValueError, match="exceeds platform limit"):
        limits.validate_simulation_duration(99999.0)

    assert limits.validate_vehicle_count(50) == 50

    with pytest.raises(ValueError, match="strictly positive"):
        limits.validate_vehicle_count(0)

    with pytest.raises(ValueError, match="exceeds platform limit"):
        limits.validate_vehicle_count(1000)

    assert limits.validate_qubo_variable_count(20) == 20

    with pytest.raises(ValueError, match="exceeds platform safety threshold"):
        limits.validate_qubo_variable_count(200)


def test_validation_helpers() -> None:
    network = Network(
        network_id="NET1",
        directed=True,
        nodes=(
            NetworkNode(node_id="I1"),
            NetworkNode(node_id="I2"),
        ),
        edges=(
            NetworkEdge(
                edge_id="E1",
                source="I1",
                target="I2",
                length_m=100.0,
                capacity=10.0,
                free_flow_speed_kph=50.0,
                travel_time_seconds=7.2,
            ),
        ),
    )

    assert validate_network_node_exists(network, "I1") == "I1"
    assert validate_network_edge_exists(network, "E1") == "E1"

    with pytest.raises(ValidationError, match="does not exist"):
        validate_network_node_exists(network, "I99")

    with pytest.raises(ValidationError, match="does not exist"):
        validate_network_edge_exists(network, "E99")

    valid_event = CongestionSpikeEvent(
        event_id="EV1",
        edge_id="E1",
        starts_at_seconds=10.0,
        duration_seconds=30.0,
    )
    assert validate_event_payload(valid_event, network) == valid_event

    invalid_event = CongestionSpikeEvent(
        event_id="EV2",
        edge_id="E99",
        starts_at_seconds=5.0,
    )
    with pytest.raises(ValidationError, match="does not exist"):
        validate_event_payload(invalid_event, network)


def test_determinism_seed_propagation() -> None:
    scenario1 = low_traffic_scenario(seed=12345)
    sim1 = TrafficSimulation(scenario1)
    obs1 = []
    for _ in range(10):
        obs1.append(sim1.step())

    scenario2 = low_traffic_scenario(seed=12345)
    sim2 = TrafficSimulation(scenario2)
    obs2 = []
    for _ in range(10):
        obs2.append(sim2.step())

    hash1 = compute_state_trajectory_hash(obs1)
    hash2 = compute_state_trajectory_hash(obs2)
    assert hash1 == hash2
    assert verify_simulation_equivalence(obs1, obs2)


def test_hybrid_optimizer_truthfulness_metadata() -> None:
    config = HybridOptimizerConfig()  # Default hybrid mode
    optimizer = HybridSignalOptimizer(config=config)

    scenario = low_traffic_scenario(seed=42)
    sim = TrafficSimulation(scenario)
    sim.step()

    from app.adaptive.observer import TrafficObserver

    observer = TrafficObserver()
    net_snap, state_snap = observer.observe(sim)

    res = optimizer.optimize(net_snap, state_snap)

    assert res.solver_name in (
        "classical_reference",
        "classical_brute_force",
        "classical_greedy",
        "fallback_fixed_time",
        "hybrid_qaoa_aer",
    )
    assert isinstance(res.fallback_used, bool)
    if res.fallback_used:
        assert res.fallback_reason is not None

