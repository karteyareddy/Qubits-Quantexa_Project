"""Dynamic traffic-event contracts."""

from enum import Enum
from typing import Self

from pydantic import Field, JsonValue, model_validator

from app.domain.base import DomainModel, Identifier


class EventType(str, Enum):
    CONGESTION = "congestion"
    ACCIDENT = "accident"
    ROAD_CLOSURE = "road_closure"
    EMERGENCY_ARRIVAL = "emergency_arrival"


class EventStatus(str, Enum):
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    RESOLVED = "resolved"
    EXPIRED = "expired"
    FAILED = "failed"


class TrafficEvent(DomainModel):
    """A scheduled, active, or resolved event without handling logic."""

    event_id: Identifier
    event_type: EventType
    starts_at_seconds: float = Field(ge=0.0)
    duration_seconds: float | None = Field(default=None, gt=0.0)
    status: EventStatus = EventStatus.SCHEDULED
    resolved_at_seconds: float | None = Field(default=None, ge=0.0)
    edge_ids: tuple[Identifier, ...] = ()
    intersection_ids: tuple[Identifier, ...] = ()
    payload: dict[str, JsonValue] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_resolution(self) -> Self:
        if self.status is EventStatus.RESOLVED and self.resolved_at_seconds is None:
            raise ValueError("resolved events require a resolution timestamp")
        if self.status is not EventStatus.RESOLVED and self.resolved_at_seconds is not None:
            raise ValueError("only resolved events may have a resolution timestamp")
        if (
            self.resolved_at_seconds is not None
            and self.resolved_at_seconds < self.starts_at_seconds
        ):
            raise ValueError("event resolution cannot precede its start")
        return self
