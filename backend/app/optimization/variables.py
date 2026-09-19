"""Decision variable mappings for Priority-Aware MTF optimization.

Binary decision variables represent route assignments:
x(v, r) = 1 if vehicle v is assigned candidate route r, else 0.
"""

from collections.abc import Sequence

from app.domain.vehicle import Vehicle


def create_subproblem_variables(
    vehicles: Sequence[Vehicle],
    candidate_routes_map: dict[str, Sequence[tuple[str, ...]]],
) -> dict[tuple[str, int], str]:
    """Create a mapping from (vehicle_id, route_idx) to deterministic variable name."""
    variable_map: dict[tuple[str, int], str] = {}
    for vehicle in vehicles:
        vid = vehicle.vehicle_id
        routes = candidate_routes_map.get(vid, ())
        for r_idx in range(len(routes)):
            var_name = f"x_{vid}_{r_idx}"
            variable_map[(vid, r_idx)] = var_name
    return variable_map


def parse_variable_name(var_name: str) -> tuple[str, int] | None:
    """Parse x_{vid}_{r_idx} back into (vehicle_id, route_idx)."""
    if not var_name.startswith("x_"):
        return None
    parts = var_name[2:].rsplit("_", 1)
    if len(parts) != 2:
        return None
    try:
        return parts[0], int(parts[1])
    except ValueError:
        return None
