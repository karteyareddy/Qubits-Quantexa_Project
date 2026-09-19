"""Route domain contracts."""

from typing import Self

from pydantic import Field, model_validator

from app.domain.base import DomainModel, Identifier


class Route(DomainModel):
    """A provider-independent route through a network."""

    route_id: Identifier
    node_ids: tuple[Identifier, ...] = Field(min_length=1)
    edge_ids: tuple[Identifier, ...] = ()
    estimated_travel_time_seconds: float = Field(ge=0.0)
    distance_m: float = Field(ge=0.0)
    score: float | None = None
    cost: float | None = Field(default=None, ge=0.0)

    @model_validator(mode="after")
    def validate_edge_count(self) -> Self:
        expected_edges = max(len(self.node_ids) - 1, 0)
        if self.edge_ids and len(self.edge_ids) != expected_edges:
            raise ValueError("route edge count must match its node sequence")
        return self
