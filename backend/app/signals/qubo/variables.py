"""Deterministic decision variable indexing for Signal-Control QUBO.

Binary decision variable x(i, p, t) = 1 if intersection i selects phase p at interval t.
Variable name format: x_{intersection_id}_P{phase_index}_T{interval_index}
"""

from collections.abc import Sequence

from app.domain.signal import SignalPhase


def create_signal_variables(
    intersection_ids: Sequence[str],
    intersection_legal_phases: dict[str, Sequence[SignalPhase]],
    horizon_intervals: int,
) -> tuple[dict[tuple[str, int, int], str], list[str]]:
    """Create deterministic variable mapping and ordered variable name list.

    Returns:
        (variable_map, variable_names) where variable_map maps (intersection_id, phase_idx, time_idx) -> var_name
    """
    variable_map: dict[tuple[str, int, int], str] = {}
    variable_names: list[str] = []

    sorted_intersections = sorted(intersection_ids)
    for intersection_id in sorted_intersections:
        phases = intersection_legal_phases.get(intersection_id, ())
        for t in range(horizon_intervals):
            for p_idx in range(len(phases)):
                var_name = f"x_{intersection_id}_P{p_idx}_T{t}"
                variable_map[(intersection_id, p_idx, t)] = var_name
                variable_names.append(var_name)

    return variable_map, variable_names


def parse_signal_variable_name(var_name: str) -> tuple[str, int, int] | None:
    """Parse x_{intersection_id}_P{phase_idx}_T{time_idx} into (intersection_id, phase_idx, time_idx)."""
    if not var_name.startswith("x_"):
        return None
    body = var_name[2:]
    parts = body.rsplit("_", 2)
    if len(parts) != 3:
        return None
    intersection_id, phase_part, time_part = parts
    if not phase_part.startswith("P") or not time_part.startswith("T"):
        return None
    try:
        p_idx = int(phase_part[1:])
        t_idx = int(time_part[1:])
        return intersection_id, p_idx, t_idx
    except ValueError:
        return None
