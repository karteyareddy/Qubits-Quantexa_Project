"""Unit tests for Stage 16 benchmarking subsystem."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from app.benchmark.aggregation import aggregate_run_results
from app.benchmark.comparison import compare_results
from app.benchmark.config import BenchmarkConfig
from app.benchmark.models import BenchmarkRunResult
from app.benchmark.reporting import (
    build_benchmark_report,
    export_report_to_csv,
    export_report_to_json,
)
from app.benchmark.scenarios import build_benchmark_scenario


def test_benchmark_config_defaults():
    config = BenchmarkConfig()
    assert config.scenario_id == "low-traffic"
    assert config.duration_seconds == 60.0
    assert config.seed == 42
    assert config.repetitions == 1


def test_build_benchmark_scenarios():
    sc_low, ev_low = build_benchmark_scenario("low-traffic", seed=42, duration_seconds=30.0)
    assert sc_low.scenario_id == "low-traffic"
    assert sc_low.duration_seconds == 30.0
    assert len(ev_low) == 0

    sc_emerg, ev_emerg = build_benchmark_scenario("emergency", seed=42, duration_seconds=30.0)
    assert sc_emerg.scenario_id == "emergency-vehicle"
    assert len(ev_emerg) == 1
    assert ev_emerg[0].event_type.value == "emergency_arrival"


def test_compare_results():
    r_c = BenchmarkRunResult(
        run_id="c1",
        scenario_id="low-traffic",
        control_strategy="fixed_time",
        seed=42,
        duration_seconds=60.0,
        metrics={"average_waiting_time_seconds": 20.0, "throughput_vph": 100.0},
        wall_clock_runtime_seconds=0.5,
    )
    r_h = BenchmarkRunResult(
        run_id="h1",
        scenario_id="low-traffic",
        control_strategy="hybrid_qaoa",
        seed=42,
        duration_seconds=60.0,
        metrics={"average_waiting_time_seconds": 15.0, "throughput_vph": 120.0},
        wall_clock_runtime_seconds=1.2,
    )

    comp = compare_results("low-traffic", r_c, r_h)
    assert comp.scenario_id == "low-traffic"
    assert "average_waiting_time_seconds" in comp.metric_deltas

    d_wait = comp.metric_deltas["average_waiting_time_seconds"]
    assert d_wait.classical_value == 20.0
    assert d_wait.hybrid_value == 15.0
    assert d_wait.absolute_delta == -5.0
    assert d_wait.relative_change_percent == -25.0


def test_aggregation():
    r1 = BenchmarkRunResult(
        run_id="r1",
        scenario_id="low",
        control_strategy="fixed_time",
        seed=42,
        duration_seconds=60.0,
        metrics={"average_waiting_time_seconds": 10.0},
        wall_clock_runtime_seconds=0.1,
    )
    r2 = BenchmarkRunResult(
        run_id="r2",
        scenario_id="low",
        control_strategy="fixed_time",
        seed=43,
        duration_seconds=60.0,
        metrics={"average_waiting_time_seconds": 20.0},
        wall_clock_runtime_seconds=0.1,
    )

    agg = aggregate_run_results([r1, r2])
    assert agg["trial_count"] == 2
    assert agg["successful_trials"] == 2
    assert agg["metrics_summary"]["average_waiting_time_seconds"]["mean"] == 15.0
    assert agg["metrics_summary"]["average_waiting_time_seconds"]["min"] == 10.0
    assert agg["metrics_summary"]["average_waiting_time_seconds"]["max"] == 20.0


def test_report_json_and_csv_export():
    r_c = BenchmarkRunResult(
        run_id="c1",
        scenario_id="low-traffic",
        control_strategy="fixed_time",
        seed=42,
        duration_seconds=60.0,
        metrics={"average_waiting_time_seconds": 20.0, "throughput_vph": 100.0},
        wall_clock_runtime_seconds=0.5,
    )
    r_h = BenchmarkRunResult(
        run_id="h1",
        scenario_id="low-traffic",
        control_strategy="hybrid_qaoa",
        seed=42,
        duration_seconds=60.0,
        metrics={"average_waiting_time_seconds": 15.0, "throughput_vph": 120.0},
        wall_clock_runtime_seconds=1.2,
    )
    comp = compare_results("low-traffic", r_c, r_h)
    report = build_benchmark_report([comp], seed=42)

    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        json_file = export_report_to_json(report, tmp_path / "test.json")
        csv_file = export_report_to_csv(report, tmp_path / "test.csv")

        assert json_file.exists()
        assert csv_file.exists()

        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)
            assert data["report_id"] == report.report_id
            assert len(data["comparisons"]) == 1
