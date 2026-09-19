"""Integration test running full closed-loop AdaptiveSimulationRunner over multiple cycles."""

from app.adaptive.config import AdaptiveConfig
from app.adaptive.service import AdaptiveSimulationRunner
from app.optimization.hybrid_models import HybridOptimizerConfig
from app.quantum.config import QAOAConfig
from app.signals.qubo.config import SignalQuboConfig
from app.simulation.scenarios import congested_traffic_scenario


def test_adaptive_simulation_runner_closed_loop_execution() -> None:
    scenario = congested_traffic_scenario(seed=42)

    # Fast 20-second run with 10-second control intervals (triggers at t=0 and t=10)
    q_cfg = SignalQuboConfig(horizon_intervals=2)
    qaoa_cfg = QAOAConfig(reps=1, shots=512, seed=42, max_iterations=15)
    hybrid_cfg = HybridOptimizerConfig(
        mode="hybrid",
        candidate_count=5,
        enable_refinement=True,
        qubo_config=q_cfg,
        qaoa_config=qaoa_cfg,
    )

    adaptive_config = AdaptiveConfig(
        control_interval_seconds=10.0,
        enabled=True,
        hybrid_config=hybrid_cfg,
    )

    runner = AdaptiveSimulationRunner(config=adaptive_config)
    result = runner.run_adaptive_simulation(
        scenario=scenario,
        duration_seconds=20.0,
        run_id="integration-test-run",
    )

    assert result.run_id == "integration-test-run"
    assert result.duration_seconds == 20.0
    assert result.optimization_count == 2  # t=0.0 and t=10.0
    assert len(result.optimization_events) == 2

    for event in result.optimization_events:
        assert event.status in ("success", "fallback")
        assert event.solver_name in ("hybrid_qaoa", "classical_reference")
        assert event.is_feasible is True
        assert event.schedule is not None
        assert event.optimization_time > 0.0

    # Verify Stage 6 ScenarioMetrics returned
    assert result.metrics.scenario_id == scenario.scenario_id
    assert result.metrics.traffic_metrics.simulation_duration_seconds == 20.0
    assert result.metrics.traffic_metrics.total_vehicles > 0
    assert result.total_optimization_time > 0.0
    assert len(result.final_signal_state) == 6
