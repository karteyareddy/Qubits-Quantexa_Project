"""Domain models for benchmark results, comparisons, and reports."""

from typing import Any

from pydantic import Field

from app.domain.base import DomainModel


class MetricDelta(DomainModel):
    """Absolute difference and relative percentage change for a metric."""

    metric_name: str
    classical_value: float
    hybrid_value: float
    absolute_delta: float = Field(description="hybrid_value - classical_value")
    relative_change_percent: float | None = Field(
        default=None, description="((hybrid_value - classical_value) / classical_value) * 100"
    )


class BenchmarkRunResult(DomainModel):
    """Detailed result snapshot from a single strategy benchmark run."""

    run_id: str
    scenario_id: str
    control_strategy: str = Field(description="fixed_time or hybrid_qaoa")
    seed: int
    duration_seconds: float
    metrics: dict[str, Any] = Field(default_factory=dict, description="Traffic & environmental metrics")
    optimization_metrics: dict[str, Any] = Field(
        default_factory=dict, description="Solver, energy, QAOA depth, fallback counts"
    )
    emergency_metrics: dict[str, Any] = Field(
        default_factory=dict, description="Emergency corridor travel and wait times"
    )
    wall_clock_runtime_seconds: float = Field(description="Actual execution duration in wall-clock time")
    status: str = Field(default="COMPLETED", description="COMPLETED or FAILED")
    failure_reason: str | None = None


class BenchmarkComparison(DomainModel):
    """Matched comparison between Classical Fixed-Time and Hybrid QAOA strategies."""

    scenario_id: str
    classical_result: BenchmarkRunResult
    hybrid_result: BenchmarkRunResult
    metric_deltas: dict[str, MetricDelta] = Field(default_factory=dict)
    summary_notes: list[str] = Field(default_factory=list)


class BenchmarkReport(DomainModel):
    """Structured report aggregating single or multi-scenario benchmark comparisons."""

    report_id: str
    created_at_timestamp: str
    environment_metadata: dict[str, Any] = Field(
        default_factory=dict, description="System info, python/qiskit version, seed, git commit"
    )
    comparisons: list[BenchmarkComparison] = Field(default_factory=list)
    summary_table: list[dict[str, Any]] = Field(default_factory=list)
