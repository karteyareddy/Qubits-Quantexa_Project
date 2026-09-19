"""Reference brute-force solver for small Signal QUBO instances (< 20 variables).

Used for ground-truth mathematical validation and testing.
"""

from collections.abc import Sequence

from app.signals.qubo.evaluator import evaluate_qubo_energy


def solve_signal_qubo_brute_force(
    Q: dict[tuple[str, str], float],
    variable_names: Sequence[str],
    constant_offset: float = 0.0,
) -> tuple[dict[str, int], float, str]:
    """Enumerate all 2^N binary assignments to find exact global minimum energy.

    Returns:
        (best_assignment, minimum_energy, best_bitstring)
    """
    n_vars = len(variable_names)
    if n_vars == 0:
        return {}, constant_offset, ""
    if n_vars > 20:
        raise ValueError(f"Brute-force solver only supports <= 20 variables (got {n_vars})")

    best_assignment: dict[str, int] = {}
    min_energy = float("inf")
    best_bitstring = ""

    num_combinations = 1 << n_vars
    for idx in range(num_combinations):
        bit_chars: list[str] = []
        assignment: dict[str, int] = {}

        for bit_pos in range(n_vars):
            bit_val = (idx >> (n_vars - 1 - bit_pos)) & 1
            var_name = variable_names[bit_pos]
            assignment[var_name] = bit_val
            bit_chars.append(str(bit_val))

        energy = evaluate_qubo_energy(Q, assignment, constant_offset)
        if energy < min_energy:
            min_energy = energy
            best_assignment = assignment
            best_bitstring = "".join(bit_chars)

    return best_assignment, min_energy, best_bitstring
