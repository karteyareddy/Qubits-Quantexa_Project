"""QAOA Quantum Circuit builder using Qiskit standard gate library."""

from collections.abc import Sequence

from qiskit import QuantumCircuit  # type: ignore[import-untyped]


def build_qaoa_circuit(
    num_qubits: int,
    h_coeffs: dict[int, float],
    J_coeffs: dict[tuple[int, int], float],
    gammas: Sequence[float],
    betas: Sequence[float],
) -> QuantumCircuit:
    """Build parameterized QAOA QuantumCircuit for depth p = len(gammas).

    Args:
        num_qubits: Number of qubits in circuit (QUBO variable count).
        h_coeffs: Single-qubit Z interaction terms.
        J_coeffs: Two-qubit ZZ interaction terms (qubit_i, qubit_j) where qubit_i < qubit_j.
        gammas: Cost layer angles for each depth p.
        betas: Mixer layer angles for each depth p.

    Returns:
        qiskit.QuantumCircuit with measurement register.
    """
    reps = len(gammas)
    if len(betas) != reps:
        raise ValueError(f"Mismatch between gammas count ({reps}) and betas count ({len(betas)})")

    qc = QuantumCircuit(num_qubits, num_qubits)

    # 1. Initial State Preparation: |+>^n via Hadamard gates
    for i in range(num_qubits):
        qc.h(i)

    # 2. Alternating Cost and Mixer layers for depth p
    for layer in range(reps):
        gamma_k = gammas[layer]
        beta_k = betas[layer]

        # Cost Unitary: exp(-i * gamma * H_C)
        # Single-qubit Z terms
        for i, h_val in h_coeffs.items():
            qc.rz(2.0 * gamma_k * h_val, i)

        # Two-qubit ZZ interaction terms
        for (i, j), J_val in J_coeffs.items():
            qc.rzz(2.0 * gamma_k * J_val, i, j)

        # Mixer Unitary: exp(-i * beta * H_M) with standard X mixer
        for i in range(num_qubits):
            qc.rx(2.0 * beta_k, i)

    # 3. Measurement of all qubits into classical registers
    qc.measure(range(num_qubits), range(num_qubits))

    return qc
