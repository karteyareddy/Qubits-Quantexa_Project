"""Vehicle domain contracts."""

from enum import Enum
from typing import Self

from pydantic import Field, model_validator

from app.domain.base import DomainModel, Identifier
from app.domain.route import Route


class VehicleType(str, Enum):
    REGULAR = "regular"
    EMERGENCY = "emergency"
    USER = "user"


class EmergencySubtype(str, Enum):
    AMBULANCE = "ambulance"
    FIRE_TRUCK = "fire_truck"
    POLICE = "police"


class VehicleState(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    WAITING = "waiting"
    ARRIVED = "arrived"


class Vehicle(DomainModel):
    """Vehicle state without movement behavior."""

    vehicle_id: Identifier
    vehicle_type: VehicleType
    origin: Identifier
    destination: Identifier
    route: Route | None = None
    candidate_routes: tuple[Route, ...] = ()
    is_emergency: bool = False
    emergency_subtype: EmergencySubtype | None = None
    priority_weight: int = Field(default=1, ge=1, le=100)
    state: VehicleState = VehicleState.PENDING
    arrival_time_seconds: float = Field(default=0.0, ge=0.0)
    completion_time_seconds: float | None = Field(default=None, ge=0.0)
    total_travel_time_seconds: float = Field(default=0.0, ge=0.0)
    current_route_index: int = Field(default=0, ge=0)
    current_node_id: Identifier | None = None
    current_edge_id: Identifier | None = None
    position_on_edge: float = Field(default=0.0, ge=0.0, le=1.0)
    speed_kph: float = Field(default=0.0, ge=0.0)
    waiting_time_seconds: float = Field(default=0.0, ge=0.0)
    stopped_time_seconds: float = Field(default=0.0, ge=0.0)
    distance_travelled_m: float = Field(default=0.0, ge=0.0)

    @model_validator(mode="after")
    def validate_emergency_identity(self) -> Self:
        type_is_emergency = self.vehicle_type is VehicleType.EMERGENCY
        if type_is_emergency != self.is_emergency:
            raise ValueError("vehicle type and emergency status must agree")
        if self.is_emergency and self.emergency_subtype is None:
            raise ValueError("emergency vehicles require an emergency subtype")
        if not self.is_emergency and self.emergency_subtype is not None:
            raise ValueError("non-emergency vehicles cannot have an emergency subtype")
        if self.state is VehicleState.ARRIVED and self.completion_time_seconds is None:
            raise ValueError("arrived vehicles require a completion timestamp")
        if self.state is not VehicleState.ARRIVED and self.completion_time_seconds is not None:
            raise ValueError("only arrived vehicles may have a completion timestamp")
        if (
            self.completion_time_seconds is not None
            and self.completion_time_seconds < self.arrival_time_seconds
        ):
            raise ValueError("vehicle completion cannot precede arrival")
        return self
