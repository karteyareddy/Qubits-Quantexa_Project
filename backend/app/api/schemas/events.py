"""API schemas for dynamic event injection and history."""

from typing import Annotated, Literal

from pydantic import BaseModel, Field


class BaseEventRequest(BaseModel):
    """Base payload fields for dynamic events."""

    timestamp: float = Field(..., ge=0.0, description="Simulation timestamp when event triggers")
    event_id: str | None = Field(default=None, description="Optional custom event ID")


class CongestionSpikeEventRequest(BaseEventRequest):
    """Request payload for congestion spike event."""

    type: Literal["congestion_spike"]
    edge_id: str = Field(..., description="Target edge ID, e.g. I1->I2")
    multiplier: float = Field(default=2.5, gt=1.0, description="Travel time multiplier")
    duration: float = Field(default=30.0, gt=0.0, description="Event duration in seconds")


class AccidentEventRequest(BaseEventRequest):
    """Request payload for traffic accident event."""

    type: Literal["accident"]
    edge_id: str = Field(..., description="Target edge ID, e.g. I2->I5")
    capacity_reduction: float = Field(
        default=0.5, gt=0.0, lt=1.0, description="Fractional capacity reduction (0.0 - 1.0)"
    )
    duration: float = Field(default=45.0, gt=0.0, description="Event duration in seconds")


class RoadClosureEventRequest(BaseEventRequest):
    """Request payload for road closure event."""

    type: Literal["road_closure"]
    target: str = Field(..., description="Target edge ID, e.g. I1->I4")
    duration: float = Field(default=60.0, gt=0.0, description="Closure duration in seconds")


class EmergencyArrivalEventRequest(BaseEventRequest):
    """Request payload for emergency vehicle arrival event."""

    type: Literal["emergency_arrival"]
    vehicle_id: str = Field(default="emergency-event-001", description="Unique vehicle ID")
    origin: str = Field(default="I1", description="Origin intersection ID")
    destination: str = Field(default="I6", description="Destination intersection ID")
    emergency_subtype: str = Field(default="AMBULANCE", description="AMBULANCE, FIRE_TRUCK, POLICE")
    priority_weight: int = Field(default=10, ge=1, description="Priority weight")


EventInjectRequest = Annotated[
    CongestionSpikeEventRequest
    | AccidentEventRequest
    | RoadClosureEventRequest
    | EmergencyArrivalEventRequest,
    Field(discriminator="type"),
]


class EventRecordResponse(BaseModel):
    """Response schema representing an event record."""

    event_id: str
    event_type: str
    timestamp: float
    duration: float
    status: str
    target: str
    details: dict[str, str | float | int | bool] = Field(default_factory=dict)
