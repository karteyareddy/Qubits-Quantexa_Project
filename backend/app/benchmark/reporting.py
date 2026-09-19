"""Benchmark report generator and JSON/CSV exporters."""

import csv
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.benchmark.models import BenchmarkComparison, BenchmarkReport


def get_environment_metadata(seed: int) -> dict[str, Any]:
    """Collect system reproducibility metadata."""
    qiskit_version = "unknown"
    try:
        import qiskit  # type: ignore[import-untyped]

        qiskit_version = getattr(qiskit, "__version__", "installed")
    except ImportError:
        pass

    qiskit_aer_version = "unknown"
    try:
        import qiskit_aer  # type: ignore[import-untyped]

        qiskit_aer_version = getattr(qiskit_aer, "__version__", "installed")
    except ImportError:
        pass

    return {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "python_version": sys.version.split()[0],
        "qiskit_version": qiskit_version,
        "qiskit_aer_version": qiskit_aer_version,
        "seed": seed,
        "git_commit": "3c4d684",
    }


def build_benchmark_report(
    comparisons: list[BenchmarkComparison], seed: int = 42
) -> BenchmarkReport:
    """Build a structured BenchmarkReport from comparisons."""
    report_id = f"report-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}"
    env_meta = get_environment_metadata(seed)

    summary_table: list[dict[str, Any]] = []
    for comp in comparisons:
        c_m = comp.classical_result.metrics
        h_m = comp.hybrid_result.metrics
        delta_obj = comp.metric_deltas.get("average_waiting_time_seconds")
        wait_delta = delta_obj.absolute_delta if delta_obj is not None else 0.0

        summary_table.append(
            {
                "scenario_id": comp.scenario_id,
                "classical_avg_wait_s": c_m.get("average_waiting_time_seconds", 0.0),
                "hybrid_avg_wait_s": h_m.get("average_waiting_time_seconds", 0.0),
                "wait_time_delta_s": wait_delta,
                "classical_throughput": c_m.get("throughput_vph", 0.0),
                "hybrid_throughput": h_m.get("throughput_vph", 0.0),
                "optimization_count": comp.hybrid_result.optimization_metrics.get(
                    "optimization_count", 0
                ),
                "fallback_count": comp.hybrid_result.optimization_metrics.get("fallback_count", 0),
                "hybrid_wall_time_s": comp.hybrid_result.wall_clock_runtime_seconds,
            }
        )

    return BenchmarkReport(
        report_id=report_id,
        created_at_timestamp=env_meta["timestamp_utc"],
        environment_metadata=env_meta,
        comparisons=comparisons,
        summary_table=summary_table,
    )


def export_report_to_json(report: BenchmarkReport, output_path: Path) -> Path:
    """Export benchmark report to a JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report.model_dump(), f, indent=2)
    return output_path


def export_report_to_csv(report: BenchmarkReport, output_path: Path) -> Path:
    """Export benchmark report summary table to a CSV file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not report.summary_table:
        return output_path

    fieldnames = list(report.summary_table[0].keys())
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in report.summary_table:
            writer.writerow(row)
    return output_path
