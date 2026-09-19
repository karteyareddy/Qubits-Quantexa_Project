"""API schemas for signal control optimization endpoints."""

from typing import Any

from pydantic import BaseModel, Field


class SignalScheduleItemSchema(BaseModel):
    """Phase assignment for a signalized intersection."""

    intersection_id: str
    selected_phase: str
    phase_duration_seconds: float = 30.0


class OptimizationRequest(BaseModel):
    """Optional configuration for manual optimization trigger."""

    solver: str = Field(default="hybrid", description="Solver type: qaoa, classical, or hybrid")
    apply_immediately: bool = Field(
        default=True, description="Apply schedule directly to current simulation policy"
    )


class OptimizationResponse(BaseModel):
    """Result from signal optimization."""

    simulation_id: str
    timestamp: float
    solver_name: str
    qubo_energy: float | None
    is_feasible: bool
    selected_schedule: dict[str, str] | None = Field(
        default=None, description="Mapping of intersection_id to phase_id"
    )
    optimization_time_seconds: float
    fallback_used: bool
    fallback_reason: str | None = None
    applied_to_simulation: bool = False
    schedule_details: list[SignalScheduleItemSchema] = Field(default_factory=list)
    raw_metrics: dict[str, Any] = Field(default_factory=dict)
