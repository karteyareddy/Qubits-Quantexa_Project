"""Integration test for Stage 16 benchmark engine and QAOA solver integration."""

from tempfile import TemporaryDirectory

from app.benchmark.config import BenchmarkConfig
from app.benchmark.runner import BenchmarkRunner
from app.benchmark.service import BenchmarkService


def test_matched_benchmark_integration_low_traffic():
    config = BenchmarkConfig(
        scenario_id="low-traffic",
        duration_seconds=30.0,
        control_interval_seconds=5.0,
        seed=42,
    )

    runner = BenchmarkRunner()
    comp = runner.run_matched_comparison(config)

    assert comp.scenario_id == "low-traffic"
    assert comp.classical_result.status == "COMPLETED"
    assert comp.hybrid_result.status == "COMPLETED"

    # Verify metrics populated
    assert "average_waiting_time_seconds" in comp.classical_result.metrics
    assert "average_waiting_time_seconds" in comp.hybrid_result.metrics
    assert "average_waiting_time_seconds" in comp.metric_deltas

    # Verify hybrid strategy exercised real optimization loop
    assert comp.hybrid_result.optimization_metrics["optimization_count"] > 0
    assert comp.hybrid_result.wall_clock_runtime_seconds > 0.0


def test_matched_benchmark_integration_emergency_corridor():
    config = BenchmarkConfig(
        scenario_id="emergency",
        duration_seconds=30.0,
        control_interval_seconds=5.0,
        seed=42,
    )

    service = BenchmarkService()
    comp = service.run_benchmark_scenario(config)

    assert comp.classical_result.status == "COMPLETED"
    assert comp.hybrid_result.status == "COMPLETED"

    with TemporaryDirectory() as tmp_dir:
        report = service.run_benchmark_suite(config, scenarios=("emergency",))
        json_file, csv_file = service.export_report(report, tmp_dir)

        assert json_file.exists()
        assert csv_file.exists()
        assert json_file.stat().st_size > 0
        assert csv_file.stat().st_size > 0
