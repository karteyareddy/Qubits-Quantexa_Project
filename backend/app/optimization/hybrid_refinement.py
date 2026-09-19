"""Classical local 1-bit flip refinement for QAOA candidate solutions."""

from collections.abc import Mapping, Sequence

from app.domain.signal import SignalPhase
from app.optimization.hybrid_models import CandidateSolution
from app.quantum.qaoa import (
    qiskit_bitstring_to_qubo_assignment,
    standard_string_to_qiskit_bitstring,
)
from app.signals.qubo.decoder import decode_signal_qubo_solution
from app.signals.qubo.evaluator import evaluate_qubo_energy


def refine_candidate_solution(
    candidate: CandidateSolution,
    Q: dict[tuple[str, str], float],
    constant_offset: float,
    variable_names: Sequence[str],
    variable_map: dict[tuple[str, int, int], str],
    intersection_legal_phases: Mapping[str, Sequence[SignalPhase]],
    horizon_intervals: int,
    max_steps: int = 50,
) -> CandidateSolution:
    """Perform deterministic local 1-bit flip search to refine candidate solution.

    Accepts neighboring bitstrings only if they maintain feasibility and strictly reduce energy.
    """
    current_bitstring = candidate.bitstring
    current_energy = candidate.qubo_energy
    current_prob = candidate.probability

    # Convert initial candidate
    qiskit_str = standard_string_to_qiskit_bitstring(current_bitstring)
    assignment = qiskit_bitstring_to_qubo_assignment(qiskit_str, variable_names)
    sched, feas, _bit = decode_signal_qubo_solution(
        assignment=assignment,
        variable_map=variable_map,
        variable_names=variable_names,
        intersection_legal_phases=intersection_legal_phases,
        horizon_intervals=horizon_intervals,
    )
    current_schedule = sched if feas.feasible else candidate.decoded_schedule
    current_feasible = feas.feasible

    n = len(variable_names)
    steps = 0

    while steps < max_steps:
        improved = False

        for i in range(n):
            # Create 1-bit flipped bitstring
            bit_list = list(current_bitstring)
            bit_list[i] = "1" if bit_list[i] == "0" else "0"
            neighbor_std = "".join(bit_list)
            neighbor_qiskit = standard_string_to_qiskit_bitstring(neighbor_std)

            neighbor_assign = qiskit_bitstring_to_qubo_assignment(neighbor_qiskit, variable_names)
            neighbor_energy = evaluate_qubo_energy(Q, neighbor_assign, constant_offset)

            neighbor_sched, neighbor_feas, _b = decode_signal_qubo_solution(
                assignment=neighbor_assign,
                variable_map=variable_map,
                variable_names=variable_names,
                intersection_legal_phases=intersection_legal_phases,
                horizon_intervals=horizon_intervals,
            )

            # Accept if neighbor is feasible and strictly lowers energy
            if neighbor_feas.feasible and neighbor_energy < current_energy - 1e-9:
                current_bitstring = neighbor_std
                current_energy = neighbor_energy
                current_schedule = neighbor_sched
                current_feasible = True
                improved = True
                break

        if not improved:
            break

        steps += 1

    return CandidateSolution(
        bitstring=current_bitstring,
        probability=current_prob,
        qubo_energy=current_energy,
        is_feasible=current_feasible,
        decoded_schedule=current_schedule,
    )
