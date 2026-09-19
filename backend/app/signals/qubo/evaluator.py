"""Exact energy evaluation for Signal-Control QUBO assignments."""

from collections.abc import Sequence


def evaluate_qubo_energy(
    Q: dict[tuple[str, str], float],
    assignment: dict[str, int],
    constant_offset: float = 0.0,
) -> float:
    """Evaluate exact energy E(x) = sum_{u, v} Q_{u,v} * x_u * x_v + constant_offset."""
    energy = constant_offset
    for (u, v), coeff in Q.items():
        val_u = assignment.get(u, 0)
        val_v = assignment.get(v, 0)
        if val_u == 1 and val_v == 1:
            energy += coeff
    return energy


def evaluate_bitstring_energy(
    Q: dict[tuple[str, str], float],
    bitstring: str,
    variable_names: Sequence[str],
    constant_offset: float = 0.0,
) -> float:
    """Evaluate exact QUBO energy from a binary bitstring."""
    if len(bitstring) != len(variable_names):
        raise ValueError(
            f"bitstring length ({len(bitstring)}) must match variable count ({len(variable_names)})"
        )

    assignment = {
        var_name: int(bitstring[idx])
        for idx, var_name in enumerate(variable_names)
    }
    return evaluate_qubo_energy(Q, assignment, constant_offset)
