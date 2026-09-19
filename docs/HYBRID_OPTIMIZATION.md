# Hybrid Quantum-Classical Signal Optimization (`docs/HYBRID_OPTIMIZATION.md`)

## 1. Overview

This document specifies the technical design of the **Hybrid Quantum-Classical Signal Optimization Subsystem** (`app.optimization`) introduced in **Stage 10**.

The hybrid optimizer orchestrates:
1. Stage 8 Signal-Control QUBO formulation
2. Stage 9 QAOA circuit simulation on Qiskit Aer
3. Top-$K$ candidate solution extraction and deterministic feasibility filtering
4. Classical local 1-bit flip refinement
5. Classical exact baseline enumeration for validation and fallback

---

## 2. Architecture & Flow Diagram

```text
Traffic State Snapshot
         ↓
Stage 8 Signal-Control QUBO
         ↓
Stage 9 QAOA Execution (Qiskit Aer)
         ↓
Candidate Distribution (Unique Bitstrings & Probabilities)
         ↓
Feasibility Filter (Exactly-One-Phase Constraint)
         ↓
Classical Local Refinement (1-Bit Flip Neighborhood Search)
         ↓
Final Valid Signal Schedule & Energy Gap Metadata
```

---

## 3. Top-K Candidate Extraction & Deterministic Sorting

From the quantum measurement counts distribution, duplicate bitstrings are aggregated. Each unique bitstring is decoded via Stage 8 `decode_signal_qubo_solution` and sorted by:

1. **Feasibility**: Feasible bitstrings satisfy $\sum_p x(i, p, t) = 1$ for all intersections and intervals.
2. **QUBO Energy**: Ascending order (lowest objective energy first).
3. **Probability**: Descending order (highest measurement frequency first).
4. **Lexicographical String Order**: Stable tie-breaking on identical energy and probability.

---

## 4. Local Classical 1-Bit Flip Refinement

For the selected best QAOA candidate:
- Evaluates the 1-bit flip neighborhood $x'_i = 1 - x_i$ for each bit index $i \in \{0, \dots, N-1\}$.
- Accepts neighboring assignment $x'$ **only** if $x'$ is feasible and strictly reduces energy ($E(x') < E(x)$).
- Iterates until local minimum is reached or `max_refinement_steps` limit is hit.

---

## 5. Execution Modes & Fallback Policy

- `hybrid`: QAOA execution $\to$ candidate extraction $\to$ local refinement $\to$ final result.
- `qaoa_only`: QAOA execution $\to$ candidate extraction $\to$ final result (without refinement).
- `classical_reference`: Exact classical brute-force enumeration.

### Fallback Policy
If QAOA samples no feasible state and `allow_classical_fallback` is enabled:
- System invokes exact classical solver.
- Result explicitly records `fallback_used = True`, `fallback_reason = "No feasible QAOA candidate sampled"`, and `solver_name = "classical_reference"`.
- A fallback result is **never** labeled as `"qaoa"`.

---

## 6. Quantum Advantage Disclaimer

> [!NOTE]
> Hybrid quantum-classical optimization provides an architectural seam for quantum exploration and classical refinement. It does not claim or imply quantum advantage over classical heuristics. Performance comparisons are evaluated strictly through controlled benchmarking.
