"""Emergency-mission contracts."""

from enum import Enum
from typing import Self

from pydantic import Field, model_validator

from app.domain.base import DomainModel, Identifier
from app.domain.route import Route


class EmergencyMissionStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EmergencyMission(DomainModel):
    """Emergency mission state without corridor behavior."""

    mission_id: Identifier
    vehicle_id: Identifier
    origin: Identifier
    destination: Identifier
    route: Route | None = None
    status: EmergencyMissionStatus = EmergencyMissionStatus.PENDING
    priority: int = Field(default=10, ge=1, le=100)
    requested_at_seconds: float = Field(ge=0.0)
    started_at_seconds: float | None = Field(default=None, ge=0.0)
    estimated_arrival_seconds: float | None = Field(default=None, ge=0.0)
    completed_at_seconds: float | None = Field(default=None, ge=0.0)

    @model_validator(mode="after")
    def validate_timeline(self) -> Self:
        if self.started_at_seconds is not None and self.started_at_seconds < self.requested_at_seconds:
            raise ValueError("mission start cannot precede its request")
        if self.status is EmergencyMissionStatus.COMPLETED and self.completed_at_seconds is None:
            raise ValueError("completed missions require a completion timestamp")
        if self.status is not EmergencyMissionStatus.COMPLETED and self.completed_at_seconds is not None:
            raise ValueError("only completed missions may have a completion timestamp")
        if (
            self.completed_at_seconds is not None
            and self.completed_at_seconds < self.requested_at_seconds
        ):
            raise ValueError("mission completion cannot precede its request")
        return self
