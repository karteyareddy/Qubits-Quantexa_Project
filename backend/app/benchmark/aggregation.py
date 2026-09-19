"""Statistical aggregation logic for repeated benchmark trials."""

import math
from typing import Any

from app.benchmark.models import BenchmarkRunResult


def aggregate_run_results(results: list[BenchmarkRunResult]) -> dict[str, Any]:
    """Aggregate a list of BenchmarkRunResults across multiple trial seeds into statistical summaries."""
    if not results:
        return {}

    metric_keys = list(results[0].metrics.keys())
    aggregated: dict[str, Any] = {
        "trial_count": len(results),
        "successful_trials": sum(1 for r in results if r.status == "COMPLETED"),
        "failed_trials": sum(1 for r in results if r.status == "FAILED"),
        "metrics_summary": {},
    }

    completed = [r for r in results if r.status == "COMPLETED"]
    if not completed:
        return aggregated

    for key in metric_keys:
        vals = [float(r.metrics.get(key, 0.0) or 0.0) for r in completed]
        n = len(vals)
        mean_val = sum(vals) / n
        sorted_vals = sorted(vals)

        if n % 2 == 1:
            median_val = sorted_vals[n // 2]
        else:
            median_val = (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2.0

        variance = sum((x - mean_val) ** 2 for x in vals) / (n - 1) if n > 1 else 0.0
        std_val = math.sqrt(variance)

        aggregated["metrics_summary"][key] = {
            "n": n,
            "mean": mean_val,
            "median": median_val,
            "min": min(vals),
            "max": max(vals),
            "std": std_val,
        }

    return aggregated
