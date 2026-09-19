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

## Stage 6 — Metrics

Implement traffic/environment metrics.

Gate:
baseline experiment produces reproducible metrics.

## Stage 7 — Existing Priority-Aware MTF migration

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

## Stage 8 — Signal QUBO

Create signal decision QUBO.

Gate:
synthetic state -> QUBO -> legal decoded signal plan.

## Stage 9 — QAOA

Implement Qiskit Aer QAOA.

Gate:
small known QUBO solves and returns metadata.

## Stage 10 — Hybrid optimizer

Connect:
traffic -> QUBO -> QAOA -> decode -> validate -> score.

Gate:
one live optimization produces a legal plan.

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
