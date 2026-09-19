"""Network domain contracts."""

from typing import Self

from pydantic import Field, JsonValue, model_validator

from app.domain.base import DomainModel, Identifier


class Coordinates(DomainModel):
    """Geographic coordinates when a network provider supplies them."""

    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)


class NetworkNode(DomainModel):
    """A normalized network node or controlled intersection."""

    node_id: Identifier
    is_intersection: bool = True
    x: float | None = None
    y: float | None = None
    coordinates: Coordinates | None = None
    metadata: dict[str, JsonValue] = Field(default_factory=dict)


class NetworkEdge(DomainModel):
    """A directed or normalized road edge."""

    edge_id: Identifier
    source: Identifier
    target: Identifier
    length_m: float = Field(gt=0.0)
    capacity: float = Field(gt=0.0)
    free_flow_speed_kph: float = Field(gt=0.0)
    travel_time_seconds: float = Field(ge=0.0)
    congestion: float = Field(default=0.0, ge=0.0)
    closed: bool = False
    metadata: dict[str, JsonValue] = Field(default_factory=dict)


class Network(DomainModel):
    """Serializable network state shared by offline and OSM providers."""

    network_id: Identifier
    scenario_id: Identifier | None = None
    directed: bool
    nodes: tuple[NetworkNode, ...] = Field(min_length=1)
    edges: tuple[NetworkEdge, ...] = ()
    metadata: dict[str, JsonValue] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_topology(self) -> Self:
        node_ids = [node.node_id for node in self.nodes]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("network node identifiers must be unique")

        edge_ids = [edge.edge_id for edge in self.edges]
        if len(edge_ids) != len(set(edge_ids)):
            raise ValueError("network edge identifiers must be unique")

        known_nodes = set(node_ids)
        for edge in self.edges:
            if edge.source not in known_nodes or edge.target not in known_nodes:
                raise ValueError("network edges must reference existing nodes")
        return self
