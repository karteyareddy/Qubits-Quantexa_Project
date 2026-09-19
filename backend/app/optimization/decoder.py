"""Solution decoding and feasibility validation for route-choice optimization."""

from collections.abc import Sequence

from app.domain.optimization import FeasibilityResult
from app.domain.vehicle import Vehicle


def decode_subproblem_solution(
    sample: dict[str, int],
    variable_map: dict[tuple[str, int], str],
    sub_vehicles: Sequence[Vehicle],
    candidate_routes_map: dict[str, Sequence[tuple[str, ...]]],
) -> tuple[dict[str, tuple[str, ...]], dict[str, int], FeasibilityResult, str]:
    """Decode binary sample into vehicle route selections and validate feasibility.

    Returns:
        (selected_routes, selected_route_indices, feasibility_result, bitstring)
    """
    selected_routes: dict[str, tuple[str, ...]] = {}
    selected_indices: dict[str, int] = {}
    violations: list[str] = []
    bit_list: list[str] = []

    # Sort variable map deterministically by vehicle_id and route_idx
    sorted_keys = sorted(variable_map.keys())
    for key in sorted_keys:
        var_name = variable_map[key]
        bit_val = sample.get(var_name, 0)
        bit_list.append("1" if bit_val == 1 else "0")

    bitstring = "".join(bit_list) if bit_list else "0"

    for vehicle in sub_vehicles:
        vid = vehicle.vehicle_id
        candidates = candidate_routes_map.get(vid, ())
        if not candidates:
            continue

        chosen_indices: list[int] = []
        for r_idx in range(len(candidates)):
            v_name: str | None = variable_map.get((vid, r_idx))
            if v_name is not None and sample.get(v_name, 0) == 1:
                chosen_indices.append(r_idx)

        if len(chosen_indices) == 0:
            violations.append(f"Vehicle {vid} selected 0 routes")
            # Default to first candidate route for execution safety
            selected_routes[vid] = candidates[0]
            selected_indices[vid] = 0
        elif len(chosen_indices) > 1:
            violations.append(
                f"Vehicle {vid} selected multiple routes: {chosen_indices}"
            )
            # Pick first selected candidate
            first_idx = chosen_indices[0]
            selected_routes[vid] = candidates[first_idx]
            selected_indices[vid] = first_idx
        else:
            idx = chosen_indices[0]
            selected_routes[vid] = candidates[idx]
            selected_indices[vid] = idx

    feasible = len(violations) == 0
    feasibility = FeasibilityResult(
        feasible=feasible,
        violations=tuple(violations),
    )

    return selected_routes, selected_indices, feasibility, bitstring
