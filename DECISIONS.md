# Decisions

## 2026-09-19 — Next.js frontend
Use Next.js + TypeScript instead of Streamlit for the final UI.

Reason:
- richer component ecosystem
- live WebSocket UI
- better visual control
- clean separation from Python quantum backend.

## 2026-09-19 — FastAPI backend
Use FastAPI as the boundary between Next.js and Python simulation/quantum services.

## 2026-09-19 — Preserve existing repository
The existing Priority-Aware MTF/QUBO/routing implementation is valuable and must be refactored rather than discarded.

## 2026-09-19 — Qiskit Aer default
Use Qiskit Aer for the default QAOA demonstration so the core project does not require paid quantum hardware.

## 2026-09-19 — Offline demo mode
Provide a deterministic six-intersection network independent of live OSM data.

## 2026-09-19 — Stage 3 routing normalization

- Follow the Stage 3 topology's seven explicit bidirectional road pairs, represented as 14 directed edges.
- Preserve directed and parallel OSM edges in the domain model instead of converting them to an undirected graph.
- For node-path search only, choose the fastest open parallel edge per direction with edge ID as a deterministic tie-breaker.
- Preserve the legacy congestion multiplier but standardize domain travel time to seconds.
- Raise an explicit routing error when no path exists; never fabricate `[origin, destination]`.
- Cache only validated JSON domain models. Do not load legacy pickle caches in the new backend.

## 2026-09-19 — Stage 4 simulation model

- Use a custom one-second discrete-time engine with no external simulator dependency.
- Reuse the Stage 2 `Vehicle` and Stage 3 `Network`/`Route` contracts.
- Treat edge capacity as maximum simultaneous vehicle occupancy, rounded down to an integer with a minimum of one.
- Derive queues from vehicles blocked from entering their next edge; do not fabricate queue values.
- Process vehicles by stable ID and use local seeded random generators for reproducibility.
- Keep intersection admission behind `IntersectionEntryPolicy`; Stage 4 permits all intersections after capacity and closure checks.
- Represent emergency identity and priority metadata without implementing emergency signal priority.

## 2026-09-19 — Stage 5 fixed-time signal baseline

- Derive controlled approaches from directed incoming network edges and node geometry.
- Use a two-axis EW/NS fixed cycle with explicit yellow and configurable all-red clearance.
- Permit intersection entry only on green; queued vehicles do not enter on yellow.
- Keep edge capacity and closure checks independent and authoritative after signal permission.
- Evaluate permission at the actual edge-crossing time within the discrete simulation step.
- Use `IntersectionEntryPolicy` as the replacement seam for later controllers; do not add adaptive or optimization behavior now.

## 2026-09-19 — Stage 6 metric semantics

- Count only spawned active and completed vehicles; pending future arrivals are excluded.
- Average waiting across all spawned vehicles so current active delay remains visible.
- Average travel only across completed vehicles using completion time minus arrival time.
- Calculate queue maximum and average from supplied state observations; never infer history from one final state.
- Estimate moving time as total travel time minus waiting time, clamped at zero to prevent double counting.
- Default prototype rates are 2.4 L/hour moving, 0.08 L/hour idle, and 2.31 kg CO2/liter; all remain configurable and explicitly uncalibrated.
- Keep metric calculation independent from controllers and optimization.

## 2026-09-19 — Stage 7 Priority-Aware MTF migration

- Migrate existing route-choice optimization into `backend/app/optimization/`.
- Preserve binary decision variables `x(v, r)` and Priority-Aware Cost Hamiltonian terms ($H_{\text{one\_route}}$, $H_{\text{route\_cost}}$, $H_{\text{congestion}}$).
- Group emergency vehicles in subproblem 0 during MTF decomposition to guarantee immediate prioritization.
- Update edge congestion factor ($1.0 + c / 20.0$) and edge travel times dynamically after each subproblem solve.
- Require explicit solver metadata (`solver_name`, `backend_name`, `execution_class`, `fallback_used`, `fallback_reason`) when falling back to classical samplers.
- Clarify that Stage 7 optimizes route allocation choice, whereas future Stage 8+ optimizes adaptive signal timing.

## 2026-09-19 — Stage 8 Signal-Control QUBO formulation

- Define binary signal variables $x(i, p, t)$ for intersection $i$, valid green phase $p$, and time interval $t \in [0, H-1]$.
- Enforce exactly-one-phase constraint $\sum_p x(i, p, t) = 1$ via quadratic penalty $A \cdot (\sum_p x(i, p, t) - 1)^2$.
- Combine traffic surrogate costs: queue length, waiting time, throughput rewards, emergency priority weighting, and inter-interval switching penalties.
- Include a deterministic energy evaluator $E(x) = x^T Q x + \text{offset}$ and brute-force validation solver for ground-truth verification.
- Decode binary solutions into serializable `SignalSchedule` domain models.
- Keep QUBO formulation strictly solver-independent without introducing QAOA or quantum circuit dependencies.

## 2026-09-19 — Stage 9 QAOA Solver for Signal-Control QUBO

- Implement parameterized QAOA quantum circuit using Qiskit 2.5.2 and Qiskit Aer 0.17.2 simulator.
- Perform exact mathematical QUBO-to-Ising mapping ($x_i = \frac{1 - z_i}{2}$) with verified energy equivalence $E_{\text{Ising}}(z) \equiv E_{\text{QUBO}}(x)$.
- Explicitly account for Qiskit big-endian measurement string formatting in `app.quantum.qaoa`.
- Filter quantum measurement distributions for feasible bitstrings satisfying Stage 8 phase constraints before selecting the minimum-energy signal schedule.
- Maintain solver transparency by explicitly reporting `solver_name="qaoa"` and `backend_name="qiskit_aer"`.

## 2026-09-19 — Stage 10 Hybrid Quantum-Classical Signal Optimizer

- Structure hybrid optimization under `backend/app/optimization/` using `HybridSignalOptimizer`.
- Extract top-K unique candidates from Qiskit measurement distributions, sorted deterministically by feasibility $\to$ energy $\to$ probability $\to$ string lexicography.
- Perform local 1-bit flip classical refinement on the best feasible QAOA candidate, accepting neighbor assignments only when feasibility is preserved and energy strictly decreases.
- Enforce strict fallback reporting: if QAOA yields no feasible candidate and classical fallback is used, `solver_name` is explicitly set to `"classical_reference"` and `fallback_used = True`.
- Compute exact energy gap relative to classical reference enumeration for small instances ($N \le 20$).

## 2026-09-19 — Stage 11 Adaptive Traffic Optimization Loop

- Structure closed-loop adaptive control under `backend/app/adaptive/` using `AdaptiveSimulationRunner`.
- Enforce snapshot immutability via `TrafficObserver`: observing traffic snapshot does not mutate simulation state before schedule application.
- Trigger optimization at explicit control boundaries $t = k \cdot \text{control\_interval\_seconds}$ via `AdaptiveScheduler`.
- Safely apply `SignalSchedule` phase decisions through `AdaptiveSignalPolicy` without bypassing signal safety rules or yellow clearance.
- Integrate Stage 6 `MetricsService` to return complete `ScenarioMetrics` alongside chronological `AdaptiveOptimizationEvent` logs.
