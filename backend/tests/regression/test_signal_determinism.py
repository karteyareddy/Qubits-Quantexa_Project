"""Regression proof for deterministic fixed-time signal simulation."""

from app.signals.policy import FixedTimeSignalPolicy, SignalSystem
from app.simulation.engine import TrafficSimulation
from app.simulation.scenarios import low_traffic_scenario


def test_fixed_time_signal_trajectory_is_reproducible() -> None:
    assert _trajectory() == _trajectory()


def _trajectory() -> tuple[dict[str, object], ...]:
    scenario = low_traffic_scenario(seed=42)
    policy = FixedTimeSignalPolicy(SignalSystem.for_network(scenario.network))
    simulation = TrafficSimulation(scenario, entry_policy=policy)
    return tuple(simulation.step().model_dump(mode="json") for _ in range(60))
