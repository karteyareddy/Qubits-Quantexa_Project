"""Qiskit Aer simulator backend execution runner."""

from qiskit import QuantumCircuit, transpile  # type: ignore[import-untyped]
from qiskit_aer import AerSimulator  # type: ignore[import-untyped]

from app.quantum.config import QAOAConfig


def execute_qaoa_circuit(
    circuit: QuantumCircuit,
    config: QAOAConfig,
) -> dict[str, int]:
    """Execute QAOA circuit on Qiskit Aer simulator with configured seed and shots.

    Returns:
        dict mapping bitstring samples to shot counts (e.g. {'0101': 512, '1010': 512}).
    """
    backend = AerSimulator()
    transpiled_circuit = transpile(
        circuit,
        backend,
        seed_transpiler=config.seed,
        optimization_level=1,
    )
    job = backend.run(
        transpiled_circuit,
        shots=config.shots,
        seed_simulator=config.seed,
    )
    result = job.result()
    counts: dict[str, int] = result.get_counts(transpiled_circuit)
    return counts
