"""Decoder converting binary QUBO samples into typed SignalSchedules."""

from collections.abc import Mapping, Sequence

from app.domain.optimization import FeasibilityResult
from app.domain.signal import SignalPhase
from app.domain.signal_qubo import IntervalSignalDecision, SignalSchedule


def decode_signal_qubo_solution(
    assignment: dict[str, int],
    variable_map: dict[tuple[str, int, int], str],
    variable_names: Sequence[str],
    intersection_legal_phases: Mapping[str, Sequence[SignalPhase]],
    horizon_intervals: int,
    interval_duration_seconds: float = 10.0,
    schedule_id: str = "schedule-1",
) -> tuple[SignalSchedule | None, FeasibilityResult, str]:
    """Decode binary assignment into a SignalSchedule and validate feasibility.

    Returns:
        (decoded_schedule, feasibility_result, bitstring)
    """
    bit_list: list[str] = []
    for var_name in variable_names:
        bit_val = assignment.get(var_name, 0)
        bit_list.append("1" if bit_val == 1 else "0")
    bitstring = "".join(bit_list) if bit_list else "0"

    decisions: list[IntervalSignalDecision] = []
    violations: list[str] = []

    sorted_intersections = sorted(intersection_legal_phases.keys())

    for intersection_id in sorted_intersections:
        phases = intersection_legal_phases[intersection_id]
        n_phases = len(phases)

        for t in range(horizon_intervals):
            chosen_indices: list[int] = []

            for p_idx in range(n_phases):
                v_name = variable_map.get((intersection_id, p_idx, t))
                if v_name is not None and assignment.get(v_name, 0) == 1:
                    chosen_indices.append(p_idx)

            if len(chosen_indices) == 1:
                idx = chosen_indices[0]
                decisions.append(
                    IntervalSignalDecision(
                        intersection_id=intersection_id,
                        interval_index=t,
                        selected_phase=phases[idx],
                        phase_index=idx,
                    )
                )
            elif len(chosen_indices) == 0:
                violations.append(
                    f"Intersection {intersection_id} selected 0 phases at interval T{t}"
                )
            else:
                violations.append(
                    f"Intersection {intersection_id} selected multiple phases {chosen_indices} at interval T{t}"
                )

    feasible = len(violations) == 0
    feasibility = FeasibilityResult(
        feasible=feasible,
        violations=tuple(violations),
    )

    if not feasible:
        return None, feasibility, bitstring

    schedule = SignalSchedule(
        schedule_id=schedule_id,
        horizon_intervals=horizon_intervals,
        interval_duration_seconds=interval_duration_seconds,
        decisions=tuple(decisions),
    )
    return schedule, feasibility, bitstring
