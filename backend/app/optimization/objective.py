"""Objective configuration and cost formulations for Priority-Aware MTF."""

from collections.abc import Sequence

from pydantic import Field

from app.domain.base import DomainModel


class PriorityMTFConfig(DomainModel):
    """Configurable weights and MTF parameters for Priority-Aware MTF optimization."""

    alpha: float = Field(default=1.0, ge=0.0)  # Route cost weight
    beta: float = Field(default=2.0, ge=0.0)   # Congestion/overlap penalty weight
    gamma: float = Field(default=50.0, ge=0.0)  # One-route constraint penalty weight
    emergency_boost: float = Field(default=10.0, ge=0.0)  # ESV green corridor multiplier
    max_subproblem_size: int = Field(default=8, ge=1)
    num_iterations: int = Field(default=3, ge=1)


def compute_route_cost(
    route: Sequence[str],
    edge_costs: dict[tuple[str, str], float],
    *,
    max_cost: float | None = None,
) -> float:
    """Compute travel cost for a node path route.

    If max_cost is provided, cost is normalized to [0, 1].
    """
    total = 0.0
    for i in range(len(route) - 1):
        edge = (route[i], route[i + 1])
        total += edge_costs.get(edge, 100.0)

    if max_cost is None:
        return total
    return total / max(max_cost, 1.0)


def normalize_edge(u: str, v: str) -> tuple[str, str]:
    """Return an undirected edge tuple for overlap evaluation."""
    return (u, v) if u <= v else (v, u)


def extract_undirected_route_edges(route: Sequence[str]) -> list[tuple[str, str]]:
    """Extract undirected edges from a node path."""
    return [normalize_edge(route[i], route[i + 1]) for i in range(len(route) - 1)]
