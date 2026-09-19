"""Domain models for demo narrative milestones, step records, and summary results."""

from typing import Any

from pydantic import Field

from app.domain.base import DomainModel


class DemoNarrativeMilestone(DomainModel):
    """Significant milestone step in the presentation narrative."""

    timestamp_seconds: float
    milestone_id: str
    title: str
    description: str
    subsystem: str = Field(description="simulation, optimization, events, emergency, metrics")
    details: dict[str, Any] = Field(default_factory=dict)


class DemoStepRecord(DomainModel):
    """Snapshot record of a single step execution during the demo run."""

    simulation_time_seconds: float
    active_vehicles_count: int
    completed_vehicles_count: int
    average_waiting_time_seconds: float
    active_events_count: int
    emergency_corridor_active: bool
    last_optimization_status: str | None = None


class DemoExecutionResult(DomainModel):
    """Complete summary output from executing the hackathon demo runner."""

    demo_id: str
    status: str = Field(default="COMPLETED", description="COMPLETED or FAILED")
    duration_seconds: float
    seed: int
    total_vehicles_spawned: int
    total_vehicles_completed: int
    average_waiting_time_seconds: float
    total_co2_emitted_kg: float
    optimizations_count: int
    qaoa_solver_name: str
    milestones: list[DemoNarrativeMilestone] = Field(default_factory=list)
    failure_reason: str | None = None
