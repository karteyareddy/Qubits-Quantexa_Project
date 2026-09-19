"""Unit tests for QAOA QuantumCircuit generation."""

import pytest
from app.quantum.circuit import build_qaoa_circuit


def test_build_qaoa_circuit_structure() -> None:
    num_qubits = 3
    h_coeffs = {0: 1.5, 1: -2.0}
    J_coeffs = {(0, 1): 3.0, (1, 2): -1.0}
    gammas = [0.5, 0.8]
    betas = [0.2, 0.4]

    circuit = build_qaoa_circuit(num_qubits, h_coeffs, J_coeffs, gammas, betas)

    assert circuit.num_qubits == 3
    assert circuit.num_clbits == 3

    # Check total depth and gate counts
    gate_names = [inst.operation.name for inst in circuit.data]
    assert "h" in gate_names
    assert "rz" in gate_names
    assert "rzz" in gate_names
    assert "rx" in gate_names
    assert "measure" in gate_names


def test_build_qaoa_circuit_mismatched_layers_raises() -> None:
    with pytest.raises(ValueError, match="Mismatch between gammas count"):
        build_qaoa_circuit(
            num_qubits=2,
            h_coeffs={},
            J_coeffs={},
            gammas=[0.1, 0.2],
            betas=[0.1],
        )
