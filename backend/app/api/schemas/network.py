"""API schemas for Network, Intersections, Edges, and Signals."""

from pydantic import BaseModel, Field


class IntersectionSchema(BaseModel):
    """Network node / intersection model."""

    intersection_id: str
    name: str
    is_signalized: bool
    position: tuple[float, float] | None = None


class EdgeSchema(BaseModel):
    """Network directed edge model."""

    edge_id: str
    source_intersection: str
    target_intersection: str
    free_flow_travel_time_seconds: float
    capacity: float
    length_meters: float = 500.0


class NetworkSchema(BaseModel):
    """Full Network topology model."""

    intersections: list[IntersectionSchema]
    edges: list[EdgeSchema]
    signalized_intersections: list[str]


class ScenarioMetadataSchema(BaseModel):
    """Metadata describing a deterministic traffic scenario."""

    scenario_id: str = Field(..., description="Unique scenario ID, e.g. low-traffic")
    name: str = Field(..., description="Human readable scenario title")
    description: str = Field(..., description="Description of vehicle count and conditions")
    duration_seconds: float = Field(..., description="Default scenario duration")
    vehicle_count: int = Field(..., description="Number of scheduled vehicles")
    emergency_vehicle_count: int = Field(..., description="Number of emergency vehicles")
