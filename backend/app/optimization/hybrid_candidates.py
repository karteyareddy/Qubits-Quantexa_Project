"""Candidate solution extraction and sorting from quantum measurement distributions."""

from collections.abc import Mapping, Sequence

from app.domain.signal import SignalPhase
from app.optimization.hybrid_models import CandidateSolution
from app.quantum.qaoa import (
    qiskit_bitstring_to_qubo_assignment,
    qiskit_bitstring_to_standard_string,
)
from app.signals.qubo.decoder import decode_signal_qubo_solution
from app.signals.qubo.evaluator import evaluate_qubo_energy


def extract_candidates(
    measurement_counts: dict[str, int],
    Q: dict[tuple[str, str], float],
    constant_offset: float,
    variable_names: Sequence[str],
    variable_map: dict[tuple[str, int, int], str],
    intersection_legal_phases: Mapping[str, Sequence[SignalPhase]],
    horizon_intervals: int,
    top_k: int = 5,
) -> list[CandidateSolution]:
    """Extract, decode, and sort top-K unique candidate solutions from measurement counts.

    Candidates are sorted deterministically:
    1. Feasible candidates first
    2. Lowest QUBO energy first
    3. Highest measurement probability first
    4. Lexicographical bitstring order for tie-breaking
    """
    total_shots = sum(measurement_counts.values())
    if total_shots == 0:
        return []

    # Aggregate by standard bitstring (index i = qubit i)
    aggregated_counts: dict[str, int] = {}
    for qiskit_str, count in measurement_counts.items():
        std_str = qiskit_bitstring_to_standard_string(qiskit_str)
        aggregated_counts[std_str] = aggregated_counts.get(std_str, 0) + count

    candidates: list[CandidateSolution] = []

    for std_str, count in aggregated_counts.items():
        qiskit_str = std_str[::-1]
        assignment = qiskit_bitstring_to_qubo_assignment(qiskit_str, variable_names)
        energy = evaluate_qubo_energy(Q, assignment, constant_offset)
        prob = count / total_shots

        sched, feasibility, _bit = decode_signal_qubo_solution(
            assignment=assignment,
            variable_map=variable_map,
            variable_names=variable_names,
            intersection_legal_phases=intersection_legal_phases,
            horizon_intervals=horizon_intervals,
        )

        candidates.append(
            CandidateSolution(
                bitstring=std_str,
                probability=prob,
                qubo_energy=energy,
                is_feasible=feasibility.feasible,
                decoded_schedule=sched if feasibility.feasible else None,
            )
        )

    # Sort candidates deterministically
    def sort_key(c: CandidateSolution) -> tuple[int, float, float, str]:
        # 0 for feasible (so True comes before False when sorting ascending)
        feas_val = 0 if c.is_feasible else 1
        # -probability so higher probability comes first
        return (feas_val, c.qubo_energy, -c.probability, c.bitstring)

    candidates.sort(key=sort_key)
    return candidates[:top_k]
