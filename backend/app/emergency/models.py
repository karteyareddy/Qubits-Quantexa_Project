"""Typed domain contracts for Emergency Green Corridor."""

from enum import Enum
from typing import Self

from pydantic import Field, model_validator

from app.domain.base import DomainModel, Identifier
from app.domain.route import Route
from app.domain.signal import SignalPhase


class CorridorStatus(str, Enum):
    """Lifecycle status of an emergency green corridor."""

    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class CorridorIntersectionReservation(DomainModel):
    """Time-bounded green phase reservation for a single controlled intersection."""

    intersection_id: Identifier
    arrival_time_seconds: float = Field(ge=0.0, description="Estimated arrival time at intersection")
    green_window_start: float = Field(ge=0.0, description="Green window start time")
    green_window_end: float = Field(ge=0.0, description="Green window end time")
    required_phase: SignalPhase = Field(description="Signal phase required for emergency movement")
    incoming_edge_id: Identifier = Field(description="Edge used to enter intersection")
    outgoing_edge_id: Identifier = Field(description="Edge used to depart intersection")

    @model_validator(mode="after")
    def validate_window(self) -> Self:
        if self.green_window_end < self.green_window_start:
            raise ValueError("green_window_end cannot be earlier than green_window_start")
        return self


class EmergencyCorridorConfig(DomainModel):
    """Configuration options for Emergency Green Corridor preemption."""

    enabled: bool = Field(default=True, description="Whether emergency corridor system is enabled")
    arrival_buffer_seconds: float = Field(
        default=3.0, ge=0.0, description="Safety lead buffer before predicted arrival"
    )
    clearance_buffer_seconds: float = Field(
        default=3.0, ge=0.0, description="Safety lag buffer after predicted passage"
    )
    max_preemption_extension_seconds: float = Field(
        default=30.0, ge=0.0, description="Maximum duration signal preemption can hold green"
    )
    resume_policy: str = Field(
        default="resume_adaptive_control",
        description="Policy after corridor release ('resume_adaptive_control', 'resume_previous_schedule')",
    )
    conflict_handling_policy: str = Field(
        default="queue",
        description="Policy when multiple emergency vehicles request corridor ('queue', 'reject', 'replace')",
    )


class EmergencyCorridor(DomainModel):
    """Time-aware green corridor reservation across multiple signalized intersections."""

    corridor_id: Identifier
    vehicle_id: Identifier
    route: Route
    intersections: tuple[CorridorIntersectionReservation, ...] = Field(
        default_factory=tuple, description="Ordered intersection green phase reservations"
    )
    status: CorridorStatus = CorridorStatus.PLANNED
    created_at_seconds: float = Field(ge=0.0)
    activated_at_seconds: float | None = Field(default=None, ge=0.0)
    released_at_seconds: float | None = Field(default=None, ge=0.0)
    failure_reason: str | None = None

    @model_validator(mode="after")
    def validate_timestamps(self) -> Self:
        if self.status in (CorridorStatus.ACTIVE, CorridorStatus.COMPLETED) and self.activated_at_seconds is None:
            raise ValueError("Active or completed corridor requires activated_at_seconds")
        if (
            self.released_at_seconds is not None
            and self.activated_at_seconds is not None
            and self.released_at_seconds < self.activated_at_seconds
        ):
            raise ValueError("Corridor release time cannot precede activation time")
        return self


class EmergencyCorridorMetrics(DomainModel):
    """Operational metrics for emergency corridor performance."""

    corridor_id: Identifier
    vehicle_id: Identifier
    activated_at_seconds: float = Field(ge=0.0)
    completed_at_seconds: float | None = Field(default=None, ge=0.0)
    duration_seconds: float = Field(default=0.0, ge=0.0)
    intersections_prioritized: int = Field(default=0, ge=0)
    emergency_waiting_seconds: float = Field(default=0.0, ge=0.0)
    emergency_travel_seconds: float = Field(default=0.0, ge=0.0)
