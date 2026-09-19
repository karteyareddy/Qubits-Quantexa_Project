"""API schemas for Emergency Green Corridor status and metrics."""

from pydantic import BaseModel, Field


class GreenWindowResponse(BaseModel):
    """Green window reservation for an intersection in the corridor."""

    intersection_id: str
    arrival_time_seconds: float
    window_start_seconds: float
    window_end_seconds: float
    incoming_approach: str
    outgoing_approach: str
    required_phase: str


class EmergencyCorridorResponse(BaseModel):
    """Emergency corridor status and details."""

    corridor_id: str
    vehicle_id: str
    route: list[str]
    intersections: list[str]
    status: str
    created_at_seconds: float
    activated_at_seconds: float | None = None
    released_at_seconds: float | None = None
    green_windows: list[GreenWindowResponse] = Field(default_factory=list)
    failure_reason: str | None = None


class EmergencyCorridorMetricsResponse(BaseModel):
    """Metrics summary for emergency corridor operations."""

    total_corridors_requested: int
    total_corridors_active: int
    total_corridors_completed: int
    total_corridors_failed: int
    average_emergency_waiting_time_seconds: float
    average_emergency_travel_time_seconds: float
