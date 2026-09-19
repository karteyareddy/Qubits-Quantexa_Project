"""Metric comparison and delta calculation logic."""

from app.benchmark.models import BenchmarkComparison, BenchmarkRunResult, MetricDelta


def compare_results(
    scenario_id: str,
    classical_result: BenchmarkRunResult,
    hybrid_result: BenchmarkRunResult,
) -> BenchmarkComparison:
    """Compute matched metric deltas between Classical Fixed-Time and Hybrid QAOA runs."""
    deltas: dict[str, MetricDelta] = {}

    c_metrics = classical_result.metrics
    h_metrics = hybrid_result.metrics

    all_keys = set(c_metrics.keys()) | set(h_metrics.keys())

    for k in sorted(all_keys):
        c_val = float(c_metrics.get(k, 0.0) or 0.0)
        h_val = float(h_metrics.get(k, 0.0) or 0.0)
        abs_delta = h_val - c_val

        rel_change = ((h_val - c_val) / c_val * 100.0) if c_val != 0.0 else None

        deltas[k] = MetricDelta(
            metric_name=k,
            classical_value=c_val,
            hybrid_value=h_val,
            absolute_delta=abs_delta,
            relative_change_percent=rel_change,
        )

    summary_notes = [
        f"Classical Fixed-Time Avg Waiting: {c_metrics.get('average_waiting_time_seconds', 0.0):.1f}s",
        f"Hybrid QAOA Avg Waiting: {h_metrics.get('average_waiting_time_seconds', 0.0):.1f}s",
        f"Optimization Count: {hybrid_result.optimization_metrics.get('optimization_count', 0)}",
        f"Fallback Count: {hybrid_result.optimization_metrics.get('fallback_count', 0)}",
    ]

    return BenchmarkComparison(
        scenario_id=scenario_id,
        classical_result=classical_result,
        hybrid_result=hybrid_result,
        metric_deltas=deltas,
        summary_notes=summary_notes,
    )
