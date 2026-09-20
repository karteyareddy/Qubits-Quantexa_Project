# Judge Q&A & Technical Defense Guide

## 1. Why use Quantum Optimization for Urban Traffic Signals?

Urban traffic signal timing across multi-intersection grid networks is an NP-hard combinatorial optimization problem. As the number of intersections and phase combinations grows, classical exact solvers scale exponentially ($O(2^N)$). Formulating signal timing as a Quadratic Unconstrained Binary Optimization (QUBO) problem allows us to map traffic control onto quantum algorithms like QAOA (Quantum Approximate Optimization Algorithm) and quantum annealers, exploring state spaces efficiently.

---

## 2. Is this running on real quantum hardware or a quantum simulator?

This prototype uses **Qiskit Aer** local quantum circuit simulation (`qiskit_aer.AerSimulator`). All QAOA circuit construction, statevector evolution, ansatz parameter tuning, and shot sampling are executed realistically via quantum circuit simulation to ensure offline reproducibility and deterministic evaluation.

---

## 3. What components are Classical vs. Quantum vs. Hybrid?

- **Classical Components**:
  - Discrete-time traffic kinematic simulation engine
  - Microscopic vehicle movement, queue tracking, and signal phase state transitions
  - Classical fixed-time signal baseline and brute-force exact QUBO reference solver
  - Local 1-bit flip post-processing refinement
- **Quantum Components**:
  - Signal-Control QUBO formulation builder
  - QAOA quantum circuit construction, parameter optimization, and measurement decoding
- **Hybrid Components**:
  - Orchestrator observing traffic state, building QUBO, executing QAOA sampling, refining top candidate bitstrings, and selecting optimal feasible signal schedules.

---

## 4. How does the Emergency Green Corridor work?

When an emergency vehicle registers a route:
1. `EmergencyCorridorPlanner` computes optimal route and predicts arrival ETAs at each downstream signalized intersection.
2. A green window $[t_{\text{start}}, t_{\text{end}}]$ is reserved for each intersection along the corridor.
3. Signal controllers override regular adaptive control to hold the required green phase during the window.
4. Non-conflicting movements remain active where safe.
5. Once the emergency vehicle clears an intersection or completes its mission, priority is released and adaptive control resumes cleanly.

---

## 5. How are benchmark comparisons evaluated truthfully?

Every benchmark trial compares a strategy (e.g. Hybrid QAOA) against a Classical Fixed-Time baseline using **identical initial state**:
- Same network topology
- Same vehicle demand and arrival schedules
- Same random seed
- Same dynamic events
- Same metric evaluation formulas (waiting time, throughput, fuel, CO₂)

If QAOA quantum simulation fails or exceeds qubit safety limits ($> 30$ qubits), the system transparently uses classical fallback, logs `fallback_used=True`, and records `fallback_reason`. Classical fallback is **never** mislabeled as quantum execution.

---

## 6. What are the key limitations of this prototype?

- **Qubit Scale**: Aer circuit simulation is computationally bounded to small/medium qubit counts (up to 30 qubits) for interactive responsiveness.
- **Single-Host Concurrency**: In-memory `asyncio.Lock` session management is designed for hackathon prototype presentation rather than multi-region distributed cluster deployment.
