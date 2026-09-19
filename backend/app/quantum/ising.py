"""Exact QUBO to Ising spin model conversion utilities."""

from collections.abc import Sequence


def qubo_to_ising(
    Q: dict[tuple[str, str], float],
    constant_offset: float,
    variable_names: Sequence[str],
) -> tuple[dict[int, float], dict[tuple[int, int], float], float]:
    """Convert binary QUBO (x in {0, 1}) to Ising model (z in {-1, +1}) using x_i = (1 - z_i)/2.

    Returns:
        (h_coeffs, J_coeffs, c_ising)
        - h_coeffs: {qubit_index: linear_coefficient}
        - J_coeffs: {(qubit_i, qubit_j): interaction_coefficient} where qubit_i < qubit_j
        - c_ising: constant energy offset such that E_Ising(z) == E_QUBO(x)
    """
    n = len(variable_names)
    var_to_idx = {name: i for i, name in enumerate(variable_names)}

    # Consolidate pair weights w_ij for i < j
    diag: list[float] = [0.0] * n
    off_diag: dict[tuple[int, int], float] = {}

    for (u, v), val in Q.items():
        if val == 0.0:
            continue
        i = var_to_idx[u]
        j = var_to_idx[v]
        if i == j:
            diag[i] += val
        else:
            if i > j:
                i, j = j, i
            off_diag[(i, j)] = off_diag.get((i, j), 0.0) + val

    h_coeffs: dict[int, float] = {}
    J_coeffs: dict[tuple[int, int], float] = {}

    c_ising = constant_offset + sum(diag[i] / 2.0 for i in range(n))

    for i in range(n):
        # Contribution to h_i from diag[i]
        h_i = -diag[i] / 2.0
        h_coeffs[i] = h_i

    for (i, j), w_ij in off_diag.items():
        J_coeffs[(i, j)] = w_ij / 4.0
        h_coeffs[i] -= w_ij / 4.0
        h_coeffs[j] -= w_ij / 4.0
        c_ising += w_ij / 4.0

    # Clean zero terms for computational efficiency
    h_coeffs = {i: val for i, val in h_coeffs.items() if abs(val) > 1e-12}
    J_coeffs = {pair: val for pair, val in J_coeffs.items() if abs(val) > 1e-12}

    return h_coeffs, J_coeffs, c_ising


def ising_energy(
    h_coeffs: dict[int, float],
    J_coeffs: dict[tuple[int, int], float],
    c_ising: float,
    z_vector: Sequence[int],
) -> float:
    """Calculate Ising energy E(z) = sum_i h_i z_i + sum_{i<j} J_{ij} z_i z_j + c_ising."""
    energy = c_ising
    for i, h_val in h_coeffs.items():
        energy += h_val * z_vector[i]
    for (i, j), J_val in J_coeffs.items():
        energy += J_val * z_vector[i] * z_vector[j]
    return energy
