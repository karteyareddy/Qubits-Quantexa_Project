"""Tests for deterministic demand and canonical Stage 4 scenarios."""

from app.routing.demo_network import build_demo_network
from app.simulation.arrivals import generate_seeded_arrivals
from app.simulation.engine import TrafficSimulation
from app.simulation.scenarios import (
    congested_traffic_scenario,
    emergency_vehicle_scenario,
    low_traffic_scenario,
)


def test_seeded_arrivals_repeat_without_global_random_state() -> None:
    network = build_demo_network(seed=42)

    first = generate_seeded_arrivals(
        network,
        count=12,
        seed=42,
        horizon_seconds=30,
        emergency_ratio=0.25,
    )
    second = generate_seeded_arrivals(
        network,
        count=12,
        seed=42,
        horizon_seconds=30,
        emergency_ratio=0.25,
    )

    assert first == second


def test_low_traffic_scenario_has_sparse_scheduled_demand() -> None:
    scenario = low_traffic_scenario()

    assert len(scenario.arrivals) == 3
    assert {arrival.arrival_time_seconds for arrival in scenario.arrivals} == {0.0, 8.0, 16.0}


def test_congested_scenario_produces_capacity_queue() -> None:
    simulation = TrafficSimulation(congested_traffic_scenario())

    assert simulation.state.counts.active == 30
    assert simulation.state.counts.waiting == 6
    assert len(simulation.state.edge_queues["I1->I2"]) == 6


def test_emergency_scenario_preserves_priority_metadata() -> None:
    simulation = TrafficSimulation(emergency_vehicle_scenario())

    simulation.run(8.0)
    emergency = next(
        vehicle for vehicle in simulation.state.active_vehicles if vehicle.is_emergency
    )

    assert emergency.vehicle_id == "emergency-001"
    assert emergency.priority_weight == 10
