"""Typed fixed-time signal configuration and approach models."""

from enum import Enum

from pydantic import Field

from app.domain.base import DomainModel, Identifier


class ApproachAxis(str, Enum):
    EAST_WEST = "EAST_WEST"
    NORTH_SOUTH = "NORTH_SOUTH"


class SignalApproach(DomainModel):
    """One incoming directed road controlled at an intersection."""

    approach_id: Identifier
    intersection_id: Identifier
    incoming_edge_id: Identifier
    source_node_id: Identifier
    axis: ApproachAxis


class SignalTiming(DomainModel):
    """Deterministic integer-second timings for a two-axis cycle."""

    green_seconds: int = Field(default=20, ge=1)
    yellow_seconds: int = Field(default=3, ge=1)
    all_red_seconds: int = Field(default=1, ge=0)

    @property
    def cycle_duration_seconds(self) -> int:
        return 2 * (self.green_seconds + self.yellow_seconds + self.all_red_seconds)
