"""API schemas for Simulation creation, state, and control."""

from typing import Any

from pydantic import BaseModel, Field


class SimulationCreateRequest(BaseModel):
    """Configuration payload for initializing a new simulation session."""

    scenario_id: str = Field(default="low-traffic", description="Scenario ID to load")
    duration_seconds: float | None = Field(
        default=None, description="Optional override for total simulation duration"
    )
    control_interval_seconds: float = Field(
        default=5.0, description="Interval between adaptive optimization updates"
    )
    seed: int = Field(default=42, description="Random seed for deterministic behavior")
    adaptive_enabled: bool = Field(default=True, description="Enable adaptive signal control")
    events_enabled: bool = Field(default=True, description="Enable dynamic events engine")
    emergency_corridor_enabled: bool = Field(
        default=True, description="Enable emergency green corridor management"
    )


class SimulationStepRequest(BaseModel):
    """Payload for stepping simulation time forward."""

    step_seconds: float = Field(
        default=1.0, gt=0.0, description="Duration in seconds to advance simulation"
    )


class VehicleStateSchema(BaseModel):
    """State representation of a vehicle in simulation."""

    vehicle_id: str
    origin: str
    destination: str
    current_edge_id: str | None
    route: list[str]
    route_index: int
    arrival_time_seconds: float
    distance_on_current_edge_meters: float
    accumulated_waiting_time_seconds: float
    speed_mps: float
    is_emergency: bool
    emergency_subtype: str | None = None
    priority_weight: int = 1
    has_arrived: bool = False
    departure_time_seconds: float | None = None


class SignalStateSchema(BaseModel):
    """Signal state representation for an intersection."""

    intersection_id: str
    current_phase: str
    time_in_phase_seconds: float
    active_green_approaches: list[str] = Field(default_factory=list)


class EdgeStateSchema(BaseModel):
    """Edge state snapshot."""

    edge_id: str
    vehicle_ids: list[str]
    vehicle_count: int
    capacity: float
    effective_capacity: float
    travel_time_multiplier: float
    is_closed: bool


class SimulationSessionResponse(BaseModel):
    """Created simulation session confirmation."""

    simulation_id: str
    status: str
    scenario_id: str
    simulation_time_seconds: float
    created_at: float


class SimulationStateSnapshot(BaseModel):
    """Detailed state snapshot of an active simulation."""

    simulation_id: str
    status: str
    simulation_time_seconds: float
    vehicles: list[VehicleStateSchema]
    signals: list[SignalStateSchema]
    edges: list[EdgeStateSchema]
    active_events: list[dict[str, Any]]
    emergency_corridors: list[dict[str, Any]]
    metrics: dict[str, Any]
