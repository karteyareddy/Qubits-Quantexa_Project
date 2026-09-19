# QAOA Quantum Optimization Engine (`docs/QAOA.md`)

## 1. Executive Summary

This document defines the technical architecture of the **Quantum Approximate Optimization Algorithm (QAOA)** solver introduced in **Stage 9** for quantum-enhanced traffic signal optimization.

The QAOA solver operates on the solver-independent **Stage 8 Signal-Control QUBO** model ($x(i, p, t) \in \{0, 1\}$).

> [!NOTE]
> Stage 9 defines quantum optimization simulation using **Qiskit** and **Qiskit Aer**. It does not claim hardware quantum supremacy or real-time QPU execution.

---

## 2. Optimization Architecture

```text
Traffic State Snapshot
         ↓
Stage 8 Signal-Control QUBO:  E_QUBO(x) = x^T Q x + c
         ↓
Ising Transformation:          E_Ising(z) = sum_i h_i z_i + sum_{i<j} J_ij z_i z_j + C_ising
         ↓
QAOA Parameterized Circuit:   |+>^n -> exp(-i gamma H_C) -> exp(-i beta H_M) -> Measure
         ↓
Qiskit Aer Simulator
         ↓
Measurement Counts & Bitstrings
         ↓
Classical Optimizer (COBYLA/SPSA) -> Update (gamma, beta)
         ↓
Feasibility Decoder & Minimum-Energy Signal Schedule
```

---

## 3. Mathematical QUBO to Ising Mapping

Binary decision variables $x_i \in \{0, 1\}$ are converted to Ising Pauli-Z eigenvalues $z_i \in \{-1, +1\}$ via:

$$x_i = \frac{1 - z_i}{2}$$

For any QUBO matrix $Q$, diagonal terms $Q_{ii}$ and symmetric pair weights $w_{ij} = Q_{ij} + Q_{ji}$ map to:

- Linear single-qubit coefficients $h_i$:
  $$h_i = -\frac{Q_{ii}}{2} - \sum_{j > i} \frac{Q_{ij} + Q_{ji}}{4} - \sum_{j < i} \frac{Q_{ji} + Q_{ij}}{4}$$

- Two-qubit interaction coefficients $J_{ij}$:
  $$J_{ij} = \frac{Q_{ij} + Q_{ji}}{4}$$

- Constant energy shift $C_{\text{Ising}}$:
  $$C_{\text{Ising}} = c + \sum_i \frac{Q_{ii}}{2} + \sum_{i < j} \frac{Q_{ij} + Q_{ji}}{4}$$

Exact energy equivalence $E_{\text{Ising}}(z) \equiv E_{\text{QUBO}}(x)$ is verified for all $2^N$ assignments on test instances.

---

## 4. Parameterized QAOA Quantum Circuit

For depth $p = \text{reps}$:

1. **Initial State Preparation**:
   $$|\psi_0\rangle = H^{\otimes n} |0\rangle^{\otimes n} = |+\rangle^{\otimes n}$$

2. **Cost Unitary Layers** ($e^{-i \gamma_k H_C}$):
   - Single-qubit $RZ(2 \gamma_k h_i)$ on qubit $i$.
   - Two-qubit $RZZ(2 \gamma_k J_{ij})$ on qubit pair $(i, j)$.

3. **Mixer Unitary Layers** ($e^{-i \beta_k H_M}$):
   - Single-qubit $RX(2 \beta_k)$ on each qubit $i$.

4. **Measurement**:
   - Quantum register measured into classical bits.

---

## 5. Qiskit Measurement Endianness

Qiskit returns bitstrings in big-endian ordering where the rightmost character `str[-1]` represents qubit 0 / variable $x_0$, and the leftmost character `str[0]` represents qubit $N-1$ / variable $x_{N-1}$.

`app.quantum.qaoa` provides deterministic reversal utilities:
- `qiskit_bitstring_to_qubo_assignment`: Maps Qiskit bitstring to variable assignment dictionary.
- `qiskit_bitstring_to_standard_string`: Reverses string so character at index $i$ corresponds to qubit $i$.

---

## 6. Solution Selection & Feasibility Filtering

QAOA samples a discrete measurement distribution. The solver:
1. Converts all observed bitstrings to QUBO assignments.
2. Computes exact Stage 8 QUBO energy $E(x)$.
3. Filters for **feasible** assignments satisfying the exactly-one-phase constraint ($\sum_p x(i, p, t) = 1$).
4. Selects the feasible bitstring with the lowest energy.

---

## 7. Verification & Quality Gates

- `backend/tests/unit/test_quantum_ising.py`: $2^N$ QUBO-to-Ising energy equivalence tests.
- `backend/tests/unit/test_quantum_circuit.py`: Circuit gate counts, depths, and parameters.
- `backend/tests/unit/test_quantum_qaoa.py`: Solver accuracy, seed reproducibility, and exact classical brute-force comparison.
- `backend/tests/integration/test_qaoa_signal_simulation.py`: Live simulation snapshot integration test.
