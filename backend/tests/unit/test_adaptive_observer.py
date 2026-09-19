"""Unit tests for TrafficObserver state snapshot extraction."""

from app.adaptive.observer import TrafficObserver
from app.signals.policy import FixedTimeSignalPolicy, SignalSystem
from app.simulation.engine import TrafficSimulation
from app.simulation.scenarios import congested_traffic_scenario


def test_traffic_observer_extracts_snapshot_without_mutating_state() -> None:
    scenario = congested_traffic_scenario(seed=42)
    policy = FixedTimeSignalPolicy(SignalSystem.for_network(scenario.network))
    sim = TrafficSimulation(scenario, entry_policy=policy)

    for _ in range(10):
        sim.step()

    time_before = sim.state.simulation_time_seconds
    active_vehicles_before = len(sim.state.active_vehicles)

    observer = TrafficObserver()
    net_snap, state_snap = observer.observe(sim)

    # Verify snapshot properties
    assert net_snap.network_id == scenario.network.network_id
    assert state_snap.simulation_time_seconds == time_before

    # Verify simulation state was unmutated
    assert sim.state.simulation_time_seconds == time_before
    assert len(sim.state.active_vehicles) == active_vehicles_before
