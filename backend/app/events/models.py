"""Typed domain models for Dynamic Traffic Events."""

from typing import Any

from pydantic import Field, model_validator

from app.adaptive.models import AdaptiveRunResult
from app.domain.base import DomainModel, Identifier
from app.domain.event import EventStatus, EventType


class EventError(Exception):
    """Base exception for dynamic event processing errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class TrafficEventBase(DomainModel):
    """Base contract for strongly typed dynamic traffic events."""

    event_id: Identifier
    event_type: EventType
    starts_at_seconds: float = Field(ge=0.0, description="Timestamp in seconds when event activates")
    duration_seconds: float | None = Field(default=None, gt=0.0, description="Duration in seconds; None if permanent")

    @property
    def timestamp(self) -> float:
        return self.starts_at_seconds

    @property
    def duration(self) -> float | None:
        return self.duration_seconds

    @property
    def target(self) -> str:
        if hasattr(self, "edge_id"):
            return str(self.edge_id)
        if hasattr(self, "origin"):
            return str(self.origin)
        return ""

    @model_validator(mode="before")
    @classmethod
    def _map_convenience_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "timestamp" in data and "starts_at_seconds" not in data:
                data["starts_at_seconds"] = data.pop("timestamp")
            if "duration" in data and "duration_seconds" not in data:
                data["duration_seconds"] = data.pop("duration")
            if "target" in data:
                target_val = data.pop("target")
                if "edge_id" not in data and cls.__name__ in (
                    "CongestionSpikeEvent",
                    "AccidentEvent",
                    "RoadClosureEvent",
                ):
                    data["edge_id"] = target_val
        return data


class CongestionSpikeEvent(TrafficEventBase):
    """Sudden demand/queue increase on a network edge."""

    event_type: EventType = EventType.CONGESTION
    edge_id: Identifier
    additional_vehicle_count: int = Field(default=5, ge=1, description="Number of demand vehicles injected")


class AccidentEvent(TrafficEventBase):
    """Accident on a network edge temporarily reducing capacity."""

    event_type: EventType = EventType.ACCIDENT
    edge_id: Identifier
    severity: float = Field(default=0.75, ge=0.0, le=1.0, description="Accident severity ratio")
    capacity_factor: float = Field(default=0.25, ge=0.0, le=1.0, description="Effective capacity ratio during accident")


class RoadClosureEvent(TrafficEventBase):
    """Temporary closure of a network edge preventing new entry."""

    event_type: EventType = EventType.ROAD_CLOSURE
    edge_id: Identifier


class EmergencyArrivalEvent(TrafficEventBase):
    """Dynamic insertion of an emergency vehicle into the simulation."""

    event_type: EventType = EventType.EMERGENCY_ARRIVAL
    vehicle_id: Identifier
    origin: Identifier
    destination: Identifier
    priority: int = Field(default=20, ge=1, le=100, description="Emergency priority weight")


class EventRecord(DomainModel):
    """Serializable record of an event's lifecycle during simulation."""

    event_id: Identifier
    event_type: EventType
    starts_at_seconds: float = Field(ge=0.0)
    duration_seconds: float | None = None
    applied_at_seconds: float | None = None
    expired_at_seconds: float | None = None
    status: EventStatus = EventStatus.SCHEDULED
    target: str = Field(description="Target edge, intersection, or vehicle identifier")
    failure_reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def scheduled_time(self) -> float:
        return self.starts_at_seconds

    @property
    def applied_time(self) -> float | None:
        return self.applied_at_seconds

    @property
    def expired_time(self) -> float | None:
        return self.expired_at_seconds


class DynamicRunResult(DomainModel):
    """Result data structure returned by DynamicSimulationRunner."""

    adaptive_result: AdaptiveRunResult = Field(description="Closed-loop adaptive simulation run outcome")
    event_history: tuple[EventRecord, ...] = Field(default_factory=tuple, description="Complete event lifecycle log")
    event_metrics: dict[str, Any] = Field(default_factory=dict, description="Event statistics dictionary")
