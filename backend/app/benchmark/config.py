"""Benchmark configuration schemas."""

from pydantic import Field

from app.domain.base import DomainModel


class BenchmarkConfig(DomainModel):
    """Typed configuration for reproducible matched benchmark execution."""

    scenario_id: str = Field(default="low-traffic", description="Scenario identifier")
    duration_seconds: float = Field(
        default=60.0, ge=10.0, description="Total simulation duration per run"
    )
    control_interval_seconds: float = Field(
        default=5.0, gt=0.0, description="Interval between adaptive signal updates"
    )
    seed: int = Field(default=42, description="Base random seed for deterministic replay")
    warmup_seconds: float = Field(
        default=0.0, ge=0.0, description="Warmup duration before metric collection"
    )
    repetitions: int = Field(
        default=1, ge=1, le=20, description="Number of repeated trials per strategy"
    )
    output_dir: str = Field(
        default="benchmark_results", description="Directory path for JSON/CSV report exports"
    )
