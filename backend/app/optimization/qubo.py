"""QUBO construction for Priority-Aware MTF route choice optimization."""

from collections import defaultdict
from collections.abc import Sequence

import dimod

from app.domain.vehicle import Vehicle
from app.optimization.objective import (
    PriorityMTFConfig,
    compute_route_cost,
    extract_undirected_route_edges,
)


def build_cost_hamiltonian(
    vehicles: Sequence[Vehicle],
    variable_map: dict[tuple[str, int], str],
    candidate_routes_map: dict[str, Sequence[tuple[str, ...]]],
    edge_costs: dict[tuple[str, str], float],
    config: PriorityMTFConfig | None = None,
) -> dict[tuple[str, str], float]:
    """Build Priority-Aware Cost Hamiltonian QUBO dictionary.

    H_cost = alpha * H_route_cost + beta * H_congestion + gamma * H_one_route
    """
    cfg = config or PriorityMTFConfig()
    Q: defaultdict[tuple[str, str], float] = defaultdict(float)

    # 1. H_one_route: each vehicle selects exactly one route
    for v in vehicles:
        vid = v.vehicle_id
        routes = candidate_routes_map.get(vid, ())
        n_routes = len(routes)
        if n_routes == 0:
            continue

        for i in range(n_routes):
            var_i = variable_map[(vid, i)]
            Q[(var_i, var_i)] += -cfg.gamma

            for j in range(n_routes):
                if i != j:
                    var_j = variable_map[(vid, j)]
                    Q[(var_i, var_j)] += cfg.gamma

    # 2. H_route_cost: prefer shorter routes, amplified for ESVs
    all_raw_costs: list[float] = []
    for v in vehicles:
        for route in candidate_routes_map.get(v.vehicle_id, ()):
            all_raw_costs.append(compute_route_cost(route, edge_costs))
    max_cost = max(all_raw_costs) if all_raw_costs else 1.0

    for v in vehicles:
        vid = v.vehicle_id
        priority = v.priority_weight
        is_emergency = v.is_emergency

        for r_idx, route in enumerate(candidate_routes_map.get(vid, ())):
            var = variable_map[(vid, r_idx)]
            route_cost = compute_route_cost(route, edge_costs, max_cost=max_cost)
            weight = cfg.alpha * priority if is_emergency else cfg.alpha
            Q[(var, var)] += weight * route_cost

    # 3. H_congestion: penalize edge overlaps (green corridor)
    edge_usage: defaultdict[tuple[str, str], list[tuple[str, int, int, bool]]] = (
        defaultdict(list)
    )

    for v in vehicles:
        vid = v.vehicle_id
        priority = v.priority_weight
        is_emergency = v.is_emergency

        for r_idx, route in enumerate(candidate_routes_map.get(vid, ())):
            for edge in extract_undirected_route_edges(route):
                edge_usage[edge].append((vid, r_idx, priority, is_emergency))

    for users in edge_usage.values():
        if len(users) <= 1:
            continue
        for i in range(len(users)):
            for j in range(i + 1, len(users)):
                vid1, r1, _p1, em1 = users[i]
                vid2, r2, _p2, em2 = users[j]

                var1 = variable_map[(vid1, r1)]
                var2 = variable_map[(vid2, r2)]

                if em1 and not em2 or em2 and not em1:
                    penalty = cfg.beta * cfg.emergency_boost
                elif em1 and em2:
                    penalty = cfg.beta * 2.0
                else:
                    penalty = cfg.beta * 1.0

                Q[(var1, var2)] += penalty

    return dict(Q)


def build_bqm(
    Q: dict[tuple[str, str], float],
) -> dimod.BinaryQuadraticModel:
    """Convert QUBO dictionary into BinaryQuadraticModel."""
    return dimod.BinaryQuadraticModel.from_qubo(Q)  # type: ignore[no-any-return]
