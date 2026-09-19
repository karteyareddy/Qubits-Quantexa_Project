"""Integration coverage from fixed-time simulation trajectory to metrics."""

from app.metrics.service import MetricsService
from app.signals.policy import FixedTimeSignalPolicy, SignalSystem
from app.simulation.engine import TrafficSimulation
from app.simulation.scenarios import emergency_vehicle_scenario


def test_metrics_evaluate_signal_controlled_demo_simulation() -> None:
    scenario = emergency_vehicle_scenario(seed=42).model_copy(
        update={"duration_seconds": 300.0}
    )
    policy = FixedTimeSignalPolicy(SignalSystem.for_network(scenario.network))
    simulation = TrafficSimulation(scenario, entry_policy=policy)
    observations = tuple(simulation.step() for _ in range(300))

    result = MetricsService().evaluate(
        scenario.scenario_id,
        simulation.state,
        observations=observations,
    )

    assert result.traffic_metrics.total_vehicles == 3
    assert result.traffic_metrics.completed_vehicles > 0
    assert result.traffic_metrics.max_queue_length >= result.traffic_metrics.final_queue_length
    assert result.emergency_metrics.emergency_total == 1
    assert result.environmental_metrics.fuel_liters > 0.0
