"""Regression proof for deterministic simulation outcome metrics."""

from app.domain.metrics import ScenarioMetrics
from app.metrics.service import MetricsService
from app.signals.policy import FixedTimeSignalPolicy, SignalSystem
from app.simulation.engine import TrafficSimulation
from app.simulation.scenarios import congested_traffic_scenario


def test_repeated_congested_signal_runs_produce_identical_metrics() -> None:
    assert _run_metrics() == _run_metrics()


def _run_metrics() -> ScenarioMetrics:
    scenario = congested_traffic_scenario(seed=42)
    policy = FixedTimeSignalPolicy(SignalSystem.for_network(scenario.network))
    simulation = TrafficSimulation(scenario, entry_policy=policy)
    observations = tuple(simulation.step() for _ in range(120))
    return MetricsService().evaluate(
        scenario.scenario_id,
        simulation.state,
        observations=observations,
    )
