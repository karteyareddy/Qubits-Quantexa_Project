"""Priority-Aware MTF (Mini-scale Traffic Flow) pipeline orchestration."""

from collections.abc import Sequence
from typing import Any

from app.domain.optimization import (
    ExecutionClass,
    FeasibilityResult,
    OptimizationPlan,
    OptimizationResult,
    OptimizationType,
    SolverMetadata,
)
from app.domain.vehicle import Vehicle
from app.optimization.decoder import decode_subproblem_solution
from app.optimization.objective import PriorityMTFConfig, compute_route_cost
from app.optimization.qubo import build_bqm, build_cost_hamiltonian
from app.optimization.solver import solve_qubo
from app.optimization.variables import create_subproblem_variables


def decompose_into_subproblems(
    vehicles: Sequence[Vehicle],
    max_subproblem_size: int = 8,
) -> tuple[tuple[Vehicle, ...], ...]:
    """Decompose vehicle set into subproblems.

    Emergency vehicles are grouped in the first subproblem for prioritization.
    """
    emergency = tuple(v for v in vehicles if v.is_emergency)
    regular = tuple(v for v in vehicles if not v.is_emergency)

    subproblems: list[tuple[Vehicle, ...]] = []
    if emergency:
        subproblems.append(emergency)

    for i in range(0, len(regular), max_subproblem_size):
        subproblems.append(regular[i : i + max_subproblem_size])

    return tuple(subproblems)


def update_edge_congestion(
    edge_costs: dict[tuple[str, str], float],
    edge_base_times: dict[tuple[str, str], float],
    edge_congestion_counts: dict[tuple[str, str], int],
    selected_routes: dict[str, tuple[str, ...]],
) -> None:
    """Update edge congestion counts and recompute edge costs after subproblem solve."""
    for route in selected_routes.values():
        for i in range(len(route) - 1):
            edge = (route[i], route[i + 1])
            edge_congestion_counts[edge] = edge_congestion_counts.get(edge, 0) + 1
            congestion_factor = 1.0 + (edge_congestion_counts[edge] / 20.0)
            base_time = edge_base_times.get(edge, 1.0)
            edge_costs[edge] = base_time * congestion_factor


def compute_solution_metrics(
    selected_routes: dict[str, tuple[str, ...]],
    vehicles: Sequence[Vehicle],
    edge_costs: dict[tuple[str, str], float],
) -> dict[str, float | int]:
    """Compute travel time metrics for selected route assignments."""
    esv_times: list[float] = []
    regular_times: list[float] = []

    for vehicle in vehicles:
        route = selected_routes.get(vehicle.vehicle_id)
        if route is None:
            continue
        cost = compute_route_cost(route, edge_costs)
        if vehicle.is_emergency:
            esv_times.append(cost)
        else:
            regular_times.append(cost)

    total_routed = len(selected_routes)
    esv_count = len(esv_times)
    regular_count = len(regular_times)
    esv_avg = sum(esv_times) / esv_count if esv_count else 0.0
    regular_avg = sum(regular_times) / regular_count if regular_count else 0.0
    total_latency = sum(esv_times) + sum(regular_times)

    return {
        "esv_avg_travel_time": esv_avg,
        "esv_total_travel_time": sum(esv_times),
        "regular_avg_travel_time": regular_avg,
        "regular_total_travel_time": sum(regular_times),
        "total_vehicles_routed": total_routed,
        "emergency_vehicles_routed": esv_count,
        "regular_vehicles_routed": regular_count,
        "aggregate_network_latency": total_latency,
    }


def run_priority_aware_mtf(
    result_id: str,
    vehicles: Sequence[Vehicle],
    candidate_routes_map: dict[str, Sequence[tuple[str, ...]]],
    edge_base_times: dict[tuple[str, str], float],
    *,
    config: PriorityMTFConfig | None = None,
    method: str = "neal",
    num_reads: int = 200,
) -> OptimizationResult:
    """Execute full Priority-Aware MTF optimization pipeline."""
    cfg = config or PriorityMTFConfig()
    current_edge_costs = dict(edge_base_times)
    edge_congestion_counts: dict[tuple[str, str], int] = {}

    final_routes: dict[str, tuple[str, ...]] = {}
    iteration_energies: list[dict[str, float | int | bool]] = []
    all_violations: list[str] = []
    any_fallback = False
    fallback_reasons: list[str] = []

    last_solver_metadata: SolverMetadata | None = None
    last_bitstring: str = "0"
    total_runtime_ms: float = 0.0

    for iteration in range(cfg.num_iterations):
        subproblems = decompose_into_subproblems(vehicles, cfg.max_subproblem_size)
        iteration_routes: dict[str, tuple[str, ...]] = {}

        for sp_idx, sub_vehicles in enumerate(subproblems):
            valid_vehicles = [
                v for v in sub_vehicles if len(candidate_routes_map.get(v.vehicle_id, ())) > 0
            ]
            if not valid_vehicles:
                continue

            var_map = create_subproblem_variables(valid_vehicles, candidate_routes_map)
            Q = build_cost_hamiltonian(
                valid_vehicles,
                var_map,
                candidate_routes_map,
                current_edge_costs,
                config=cfg,
            )
            bqm = build_bqm(Q)

            sample, energy, solver_meta, fallback_used, fallback_reason = solve_qubo(
                bqm,
                method=method,
                num_reads=num_reads,
            )

            last_solver_metadata = solver_meta
            runtime_val = solver_meta.parameters.get("runtime_ms", 0.0)
            if isinstance(runtime_val, (int, float)):
                total_runtime_ms += float(runtime_val)

            if fallback_used:
                any_fallback = True
                if fallback_reason and fallback_reason not in fallback_reasons:
                    fallback_reasons.append(fallback_reason)

            iteration_energies.append({
                "iteration": iteration,
                "subproblem": sp_idx,
                "energy": energy,
                "num_vehicles": len(valid_vehicles),
                "has_emergency": any(v.is_emergency for v in valid_vehicles),
            })

            selected, _indices, feasibility, bitstring = decode_subproblem_solution(
                sample,
                var_map,
                valid_vehicles,
                candidate_routes_map,
            )

            if not feasibility.feasible:
                all_violations.extend(feasibility.violations)

            last_bitstring = bitstring
            iteration_routes.update(selected)
            update_edge_congestion(
                current_edge_costs,
                edge_base_times,
                edge_congestion_counts,
                selected,
            )

        final_routes.update(iteration_routes)

    solution_metrics = compute_solution_metrics(
        final_routes,
        vehicles,
        current_edge_costs,
    )

    final_violations: list[str] = []
    for vehicle in vehicles:
        vid = vehicle.vehicle_id
        candidates = candidate_routes_map.get(vid, ())
        if candidates and vid not in final_routes:
            final_violations.append(f"Vehicle {vid} has no assigned route")

    feasible = len(final_violations) == 0
    feasibility_res = FeasibilityResult(
        feasible=feasible,
        violations=tuple(final_violations),
    )

    plan_decisions: dict[str, Any] = {
        vid: list(route) for vid, route in sorted(final_routes.items())
    }

    plan = OptimizationPlan(
        plan_id=f"plan-{result_id}",
        optimization_type=OptimizationType.ROUTE,
        decisions=plan_decisions,
    )

    if last_solver_metadata is None:
        last_solver_metadata = SolverMetadata(
            solver_name="empty",
            backend_name="none",
            execution_class=ExecutionClass.CLASSICAL,
        )

    if any_fallback:
        execution_class = ExecutionClass.CLASSICAL_FALLBACK
        solver_metadata = SolverMetadata(
            solver_name=last_solver_metadata.solver_name,
            backend_name=last_solver_metadata.backend_name,
            execution_class=execution_class,
            parameters=last_solver_metadata.parameters,
        )
        combined_reason = "; ".join(fallback_reasons) if fallback_reasons else "Fallback engaged"
    else:
        solver_metadata = last_solver_metadata
        combined_reason = None

    last_energy = iteration_energies[-1]["energy"] if iteration_energies else 0.0

    return OptimizationResult(
        result_id=result_id,
        optimization_type=OptimizationType.ROUTE,
        solver=solver_metadata,
        objective_value=float(solution_metrics["aggregate_network_latency"]),
        energy=float(last_energy),
        runtime_ms=total_runtime_ms,
        feasible=feasible,
        feasibility=feasibility_res,
        fallback_used=any_fallback,
        fallback_reason=combined_reason,
        decoded_plan=plan,
        selected_bitstring=last_bitstring,
        metadata={
            "solution_metrics": dict(solution_metrics),
            "iteration_energies": list(iteration_energies),  # type: ignore[arg-type]
            "config": cfg.model_dump(),
            "method": method,
        },
    )
