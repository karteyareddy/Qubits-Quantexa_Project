"""Vehicle-entry policy extension point for future signal control."""

from dataclasses import dataclass
from typing import Protocol

from app.domain.network import NetworkEdge
from app.domain.vehicle import Vehicle
from app.simulation.models import SimulationState


class IntersectionEntryPolicy(Protocol):
    """Decide whether a vehicle may cross into its next edge."""

    def can_enter_next_edge(
        self,
        vehicle: Vehicle,
        next_edge: NetworkEdge,
        state: SimulationState,
    ) -> bool: ...


@dataclass(frozen=True)
class PermitAllIntersections:
    """Stage 4 policy; edge capacity remains enforced by the engine."""

    def can_enter_next_edge(
        self,
        vehicle: Vehicle,
        next_edge: NetworkEdge,
        state: SimulationState,
    ) -> bool:
        return True
