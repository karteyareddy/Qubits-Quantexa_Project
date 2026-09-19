"""Configuration models for Closed-Loop Adaptive Traffic Control."""

from pydantic import Field

from app.domain.base import DomainModel
from app.optimization.hybrid_models import HybridOptimizerConfig


class AdaptiveConfig(DomainModel):
    """Configuration options for closed-loop adaptive traffic signal optimization."""

    control_interval_seconds: float = Field(
        default=10.0, ge=1.0, le=300.0, description="Interval in seconds between optimization cycles"
    )
    optimization_horizon_intervals: int = Field(
        default=1, ge=1, le=10, description="Number of future discrete decision intervals in QUBO horizon"
    )
    optimization_interval_seconds: float = Field(
        default=10.0, ge=1.0, le=60.0, description="Duration of each decision interval in seconds"
    )
    enabled: bool = Field(default=True, description="Whether adaptive optimization loop is active")
    fail_on_optimization_error: bool = Field(
        default=False, description="If True, raises error on optimization failure; if False, retains previous schedule"
    )
    fallback_action: str = Field(
        default="retain_previous_schedule", description="Fallback action on optimization error ('retain_previous_schedule', 'fixed_time')"
    )
    minimum_signal_hold_seconds: float = Field(
        default=5.0, ge=0.0, description="Minimum duration a signal phase must be held before changing"
    )
    hybrid_config: HybridOptimizerConfig = Field(default_factory=HybridOptimizerConfig)
