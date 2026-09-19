# Sequential Implementation Plan

## Rule

Do not attempt the whole project in one pass.

For every stage:
Inspect -> Implement -> Test -> Fix -> Gate -> Continue.

Never skip a gate.

## Stage 0 — Repository audit

Run the existing project first.

Deliver:
- `REPOSITORY_AUDIT.md`
- `MIGRATION_PLAN.md`

Do not change architecture before understanding:
- app.py
- priority_aware_mtf.py
- traffic_simulator.py
- network_builder.py
- visualization.py
- solver modules if present
- legacy/
- requirements
- package-lock

Gate: audit identifies what is reusable vs replaceable.

## Stage 1 — Documentation and monorepo skeleton

Status: Complete (2026-09-19)

Create:
```text
frontend/
backend/
docs/
```

Keep old files temporarily for migration.

Gate:
- frontend starts
- backend health endpoint starts

Verified:
- Next.js development server returned HTTP 200 with the Stage 1 homepage.
- FastAPI `GET /health` returned `{"status":"ok"}`.
- Frontend lint and production build passed.

## Stage 2 — Backend domain extraction

Status: Complete (2026-09-19)

Create Pydantic/domain models and service interfaces.

Gate:
unit tests pass.

Verified:
- 22 Stage 2 unit tests pass.
- Ruff passes for `backend`.
- Mypy passes for `backend/app`.
- FastAPI `GET /health` still returns `{"status":"ok"}`.

## Stage 3 — Migrate existing network/routing

Move/refactor existing NetworkX/OSMnx logic.

Preserve candidate route generation and caching where useful.

Gate:
demo network and OSM mode both produce a common network contract.

Verified:
- Deterministic six-intersection demo network has 14 directed edges.
- Mocked OSM normalization returns the shared `Network` contract.
- Candidate routes are bounded, connected, travel-time ordered, and never fabricated.
- JSON cache handles misses, hits, corruption, and disabled operation.
- 37 unit, 2 integration, and 3 regression tests pass.
- Ruff passes for `backend`.
- Mypy passes for `backend/app`.
- FastAPI `GET /health` still returns `{"status":"ok"}`.
- Two demo-routing smoke runs produced the same SHA-256 digest.

## Stage 4 — Migrate traffic simulation

Refactor existing traffic simulator into backend services.

Gate:
deterministic 60-second simulation passes.

Verified:
- Stage 3 demo-network routes drive the simulation without a duplicate graph model.
- Scheduled and locally seeded arrivals are deterministic.
- Vehicle movement, edge transitions, completion, capacity blocking, queues, waiting, and emergency identity are covered.
- Low-traffic, congested, and emergency-vehicle scenarios are available.
- Repeated 60-second congested trajectories produce the same SHA-256 digest.
- 50 unit, 3 integration, and 4 regression tests pass.
- Ruff passes for `backend`.
- Mypy passes for `backend/app`.

## Stage 5 — Signals

Implement:
- signal phases
- fixed controller
- adaptive controller interface
- safety transitions

Gate:
vehicles respond correctly to green/red.

Verified:
- Incoming directed network edges map deterministically to signal approaches.
- Fixed-time EW/NS phases expose explicit red, yellow, green, and all-red states.
- Conflicting approach axes are never permitted simultaneously.
- Vehicles wait at red/yellow, cross on green, and remain blocked by full downstream edges.
- Signal delay contributes to queues and waiting time without double counting.
- Repeated 60-second signal-controlled trajectories produce the same SHA-256 digest.
- 62 unit, 7 integration, and 5 regression tests pass.
- Ruff passes for `backend`.
- Mypy passes for `backend/app`.

## Stage 6 — Metrics

Implement traffic/environment metrics.

Gate:
baseline experiment produces reproducible metrics.

Verified:
- Spawned, completed, active, completion-rate, throughput, waiting, and completed-trip travel metrics are deterministic.
- Queue maximum and average use real supplied trajectory observations; final queue uses the final state.
- Per-vehicle, emergency, edge, and intersection-approach results are typed and serializable.
- Fuel and CO2 are explicit configurable prototype estimates with zero-safe per-vehicle values.
- Repeated congested fixed-time runs produce identical metrics and the same SHA-256 digest.
- 72 unit, 8 integration, and 6 regression tests pass.
- Ruff passes for `backend`.
- Mypy passes for `backend/app`.

## Stage 7 — Existing Priority-Aware MTF migration

Status: Complete (2026-09-19)

Refactor existing `priority_aware_mtf.py` logic into a clean optimization module.

Preserve:
- priority weighting
- emergency boost
- decomposition
- congestion feedback
- route selection
- existing classical/D-Wave adapters where practical.

Gate:
old route optimization behavior has regression tests.

Verified:
- Decision variables x(v, r), QUBO terms, subproblem decomposition, and congestion feedback migrated to `backend/app/optimization/`.
- Emergency vehicles are grouped into subproblem 0 for immediate priority.
- Solvers support transparent fallback metadata (`requested_solver`, `actual_solver`, `fallback_used`, `fallback_reason`, `execution_class`).
- Legacy regression tests confirm identical route selections and energy matching against `priority_aware_mtf.py`.
- 81 unit, 9 integration, and 7 regression tests pass.
- Ruff passes for `backend`.
- Mypy passes for `backend/app`.

## Stage 8 — Signal QUBO

Status: Complete (2026-09-19)

Create signal decision QUBO.

Gate:
synthetic state -> QUBO -> legal decoded signal plan.

Verified:
- Binary decision variables x(i, p, t) defined with deterministic index naming in `backend/app/signals/qubo/variables.py`.
- Exactly-one-phase constraint A*(sum_p x(i,p,t) - 1)^2 and surrogate traffic cost terms (queue, waiting, throughput, emergency, switching) built in `SignalQuboBuilder`.
- Exact energy evaluator and brute-force reference solver validate matrix ground truth.
- Solution decoder produces serializable `SignalSchedule` domain models.
- Hand-checkable 1-intersection 2-phase expansion unit test verifies exact polynomial coefficients.
- 86 unit, 10 integration, and 7 regression tests pass.
- Ruff passes for `backend`.
- Mypy passes for `backend/app`.

## Stage 9 — QAOA

Status: Complete (2026-09-19)

Implement Qiskit Aer QAOA.

Gate:
small known QUBO solves and returns metadata.

Verified:
- `QAOAConfig` and `QAOAResult` typed domain models created in `backend/app/quantum/`.
- Exact QUBO-to-Ising conversion utility maps $x_i = (1 - z_i)/2$ with verified energy equivalence $E_{\text{Ising}}(z) \equiv E_{\text{QUBO}}(x)$.
- Parameterized QAOA quantum circuit builder constructs depth-$p$ layers using Qiskit 2.5.2 standard gates (`h`, `rz`, `rzz`, `rx`, `measure`).
- `QAOASolver` executes simulation on Qiskit Aer 0.17.2, optimizes parameters via COBYLA, and reverses Qiskit big-endian measurement bitstrings.
- Quantum output distributions are filtered for feasible signal phase assignments, returning typed `SignalSchedule` and complete execution metadata (`solver_name="qaoa"`, `backend_name="qiskit_aer"`).
- 90 unit, 11 integration, and 7 regression tests pass.
- Ruff passes for `backend`.
- Mypy passes for `backend/app`.

## Stage 10 — Hybrid optimizer

Status: Complete (2026-09-19)

Connect:
traffic -> QUBO -> QAOA -> decode -> validate -> score.

Gate:
one live optimization produces a legal plan.

Verified:
- `HybridOptimizerConfig`, `CandidateSolution`, and `HybridOptimizationResult` domain models implemented.
- Top-K unique candidate extraction with deterministic sorting (feasibility $\to$ energy $\to$ probability $\to$ string lexicography) in `hybrid_candidates.py`.
- Local 1-bit flip classical refinement in `hybrid_refinement.py` preserving feasibility while improving energy.
- `HybridSignalOptimizer` orchestrates `hybrid`, `qaoa_only`, and `classical_reference` execution modes.
- Transparent classical fallback policy correctly identifies solver identity as `classical_reference` when invoked.
- 94 unit, 12 integration, and 7 regression tests pass.
- Ruff passes for `backend`.
- Mypy passes for `backend/app`.

## Stage 11 — Adaptive simulation

Apply optimized plans every interval.

Gate:
300-second simulation runs without illegal transitions.

## Stage 12 — Events

Implement congestion, accident, closure, emergency arrival.

Gate:
each event changes state and triggers appropriate handling.

## Stage 13 — Emergency corridor

Implement routing, priority signals, tracking, restoration.

Gate:
emergency reaches destination and previous controller resumes.

## Stage 14 — FastAPI REST/WebSocket

Expose contracts in API.md.

Gate:
frontend can start/pause/step/read state/run optimization.

## Stage 15 — Next.js UI

Build:
Dashboard, Simulation, Quantum Lab, Emergency, Events, Analytics, Settings.

Gate:
all pages load with live backend state.

## Stage 16 — Benchmarking

Run matched baseline/hybrid experiments.

Gate:
comparison export generated.

## Stage 17 — Hardening

Run:
```bash
pytest -q
pytest --cov=backend/app
ruff check backend
mypy backend/app
npm run lint
npm run build
```

Gate: all pass.

## Stage 18 — Deployment

Add Dockerfiles/docker-compose and deployment docs.

Gate: clean build works.

## Stage 19 — Demo polish

Run complete judge flow:
normal -> congestion -> QAOA -> optimized signals -> emergency -> corridor -> restoration -> analytics.
