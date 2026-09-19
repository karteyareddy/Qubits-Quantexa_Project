# Migration Plan

## 1. Purpose and Constraints

This plan migrates the existing route-optimization prototype into the architecture defined by `PRD.md` and `ARCHITECTURE.md` without discarding useful algorithms or misrepresenting their behavior.

```text
Next.js + TypeScript
        |
        | REST + WebSocket
        v
FastAPI + Python
        |
        +-- traffic simulation + signals + events + metrics
        +-- NetworkX routing + optional OSMnx
        +-- route QUBO + signal QUBO
        +-- Qiskit Aer/QAOA + explicit classical fallback
        v
Optimization results and experiment exports
```

This document is a plan only. It does not authorize implementation during Stage 0. In particular:

- keep the root Streamlit application operational until backend and frontend parity is verified;
- characterize existing algorithms before moving or changing them;
- keep route selection and signal control as separate optimization models;
- make every quantum/classical backend and fallback explicit in result metadata;
- do not move Qiskit or Python domain logic into Next.js;
- do not claim quantum advantage from benchmark output;
- do not migrate generated cache artifacts as source code.

## 2. Disposition Definitions

- **Preserve:** retain the file or behavior substantially as-is, with path/link updates if needed.
- **Refactor:** retain useful behavior but split, type, validate, or relocate it behind the final architecture.
- **Replace:** implement the same user-facing or operational responsibility using the target technology after contracts are stable.
- **Deprecate:** keep temporarily for reference/rollback, remove or archive only after the relevant migration gate passes.

## 3. File-by-File Migration Matrix

### 3.1 Active implementation

| Existing file | Action | Final location | Reason | Dependencies | Migration order |
|---|---|---|---|---|---|
| `app.py` | **Deprecate** | Temporary: `legacy/streamlit/app.py`; final: removed after verified parity | Streamlit is forbidden in the final frontend, but the file is the only current orchestration/UI reference. Keep it unchanged through backend extraction and Next.js verification. | Migrated network, scenario, route optimization, metrics, API, all Next.js pages, end-to-end judge flow | Start deprecation in Stage 14-15; archive/remove only after Stage 19 verification |
| `network_builder.py` | **Refactor** | `backend/app/routing/providers/osm.py`, `backend/app/routing/demo_network.py`, `backend/app/routing/normalization.py`, `backend/app/routing/routes.py`, `backend/app/routing/cache.py` | Preserve OSMnx, edge preparation, OD/candidate route behavior, and provider fallbacks while separating network I/O, deterministic demo construction, routing, and caching. | Domain graph models, settings, seeded randomness, cache policy, regression tests | Stage 3 |
| `traffic_simulator.py` | **Refactor** | Static generation: `backend/app/simulation/demand.py`; typed records: `backend/app/domain/vehicles.py`; real engine: `backend/app/simulation/engine.py` | Current code generates demand but does not simulate traffic. Preserve emergency labels and route attachment semantics while implementing the required tick engine separately. | Domain models, common network contract, seeded scenario configuration | Stages 2 and 4 |
| `priority_aware_mtf.py` | **Refactor** | `backend/app/optimization/routing/qubo.py`, `decomposition.py`, `decoder.py`, `service.py`; shared evaluation in `backend/app/metrics/routing.py`; adapters in `backend/app/optimization/solvers/` | Core reusable asset. Split QUBO formulation, decomposition, solving, validation, congestion feedback, and benchmark concerns. Preserve characterized behavior before correcting identified issues. | Typed vehicles/routes, graph contract, regression fixtures, solver result model, explicit fallback metadata | Characterize in Stages 2-3; migrate in Stage 7 |
| `visualization.py` | **Replace** | `frontend/components/network/NetworkCanvas.tsx`, `RouteLayer.tsx`, `VehicleMarker.tsx`, and optional map adapter under `frontend/lib/map/` | Folium objects cannot cross the frontend/backend boundary. Preserve route colors, marker meanings, and map-data requirements as React/MapLibre-or-Leaflet behavior. | Typed API state, network serialization, WebSocket store, selected map library | Stage 15; retain old module until UI parity |

### 3.2 Legacy implementation

| Existing file | Action | Final location | Reason | Dependencies | Migration order |
|---|---|---|---|---|---|
| `legacy/priority_logic.py` | **Deprecate** | `docs/archive/legacy-code/priority_logic.py` or Git history after regression extraction | Not imported. Route scoring and corridor-edge rules may supply fixtures, but they do not implement a signal corridor. | Stage 7 regression review and Stage 13 emergency design | Review in Stage 7; archive after Stage 13 gate |
| `legacy/qubo_builder.py` | **Deprecate** | `docs/archive/legacy-code/qubo_builder.py` or Git history after regression extraction | Superseded by `priority_aware_mtf.py`; retaining a second production formulation would create ambiguity. | Active route-QUBO regression suite | Archive after Stage 7 gate |
| `legacy/solver.py` | **Refactor**, then **Deprecate** | Useful adapter behavior moves to `backend/app/optimization/solvers/classical.py` and `dwave.py`; original goes to archive/history | The dispatch pattern and six backend concepts are useful, but the module duplicates active code and hides fallback state. | Solver protocol/result model, optional D-Wave extras, fallback tests | Adapter extraction in Stages 7 and 9-10; archive after Stage 10 |

### 3.3 Root documentation

| Existing file | Action | Final location | Reason | Dependencies | Migration order |
|---|---|---|---|---|---|
| `AGENTS.md` | **Preserve** | `AGENTS.md` | Repository-level agent rules must continue to apply to the full tree. Add scoped files later only when necessary. | None | Continuous |
| `README.md` | **Refactor** | `README.md` | Keep the root entry point, but update commands only as each application becomes real. During migration it must clearly distinguish legacy and target run paths. | Working Stage 1 skeleton, then validated final build | Stages 1, 15, 18-19 |
| `PRD.md` | **Preserve** | `docs/PRD.md` after links are updated; keep root during active staged migration if tooling expects it | Product source of truth should live with durable product documentation, but relocation must not break operating instructions. | Documentation link update | Stage 18 or retain at root permanently |
| `TASKS.md` | **Preserve** | `TASKS.md` during migration; optionally `docs/TASKS.md` after Stage 19 | It is the active migration gate tracker and should remain easy to discover. | Completed stage evidence | Update after each future gate; optional move after Stage 19 |
| `ARCHITECTURE.md` | **Refactor** | `docs/ARCHITECTURE.md` | Expand the target diagram with implemented module boundaries and runtime contracts as stages land. | Domain/service/API implementation | Initial move Stage 1; updates throughout |
| `TECH_STACK.md` | **Preserve/Refactor** | `docs/TECH_STACK.md` | Preserve decisions; add validated pinned versions after clean installations. | Backend and frontend installs | Move Stage 1; pin/update Stages 17-18 |
| `QUANTUM_SPEC.md` | **Preserve/Refactor** | `docs/QUANTUM_SPEC.md` | Keep route-vs-signal distinction; later add exact implemented encoding, normalization, feasibility, and solver metadata. | Signal QUBO and QAOA validation | Move Stage 1; update Stages 8-10 |
| `SIMULATION_SPEC.md` | **Preserve/Refactor** | `docs/SIMULATION_SPEC.md` | Becomes the implemented simulation contract and deterministic-fixture reference. | Domain and simulation tests | Move Stage 1; update Stages 4-6 and 11-13 |
| `UI_SPEC.md` | **Preserve/Refactor** | `docs/UI_SPEC.md` | Source for Next.js page/component behavior; update only with approved implementation decisions. | API/WebSocket contracts and UI build | Move Stage 1; update Stage 15 |
| `API.md` | **Refactor** | `docs/API.md` | Convert draft endpoints and event envelopes into versioned request/response schemas that match FastAPI and generated OpenAPI. | Pydantic domain schemas and service commands | Move Stage 1; finalize Stage 14 |
| `DATABASE.md` | **Refactor** | `docs/DATA_MODEL.md` | It currently describes runtime entities more than a database. Align it to domain models; retain optional SQLite as deferred scope. | Stage 2 domain models | Stage 2 |
| `DECISIONS.md` | **Preserve** | `docs/DECISIONS.md` | Continue as append-only architectural decision log, including any stop-condition findings. | None | Move Stage 1; ongoing |
| `DEPLOYMENT.md` | **Refactor** | `docs/DEPLOYMENT.md` | Keep intended topology; replace speculative commands with verified local/container instructions. | Working Dockerfiles, compose, production settings | Stage 18 |
| `DOCUMENTATION_MAP.md` | **Refactor** | `docs/README.md` | A docs-directory index is clearer once files move. | Final documentation paths | Stage 1 and final Stage 19 pass |
| `MIGRATION_RUNBOOK.md` | **Preserve** | `docs/MIGRATION_RUNBOOK.md` | Continue to govern staged execution and gates. | Updated links/commands | Stage 1 |
| `SECURITY.md` | **Refactor** | `docs/SECURITY.md` | Preserve requirements and record concrete controls, limits, threat assumptions, and deployment validation. | Settings, Pydantic, API, solver limits, deployment | Move Stage 1; implement/update Stages 14, 17-18 |
| `TESTING.md` | **Refactor** | `docs/TESTING.md` | Turn the test strategy into commands, test layout, fixtures, coverage expectations, and known external-test markers. | Test suites and CI | Move Stage 1; update every stage; finalize Stage 17 |
| `SKILLS.md` | **Preserve** | `docs/ENGINEERING_PRACTICES.md` | Content is durable engineering guidance rather than executable configuration. | Link updates | Stage 1 |
| `CODEX_FIRST_PROMPT.md` | **Deprecate** | `docs/archive/CODEX_FIRST_PROMPT.md` | Stage 0 bootstrap prompt has served its purpose; preserve only as project history. | Approval of audit/plan | After Stage 0 approval |
| `GEMINI_ROLE.md` | **Preserve** | `docs/review/GEMINI_ROLE.md` | Retain as a later review protocol, separate from implementation instructions. | Stage 19 completion | Stage 1 move; use after Stage 19 |
| `doc.txt` | **Deprecate** | `docs/archive/original-project-notes.md` after correcting encoding or preserve via Git history | Informal claims are not an authoritative specification and can overstate quantum execution. Keep only as provenance. | `REPOSITORY_AUDIT.md` and quantum-honesty review | Archive after Stage 0 approval |
| `REPOSITORY_AUDIT.md` | **Preserve** | `docs/REPOSITORY_AUDIT.md` after Stage 1 documentation move | Baseline record for migration and review. | Link updates | Created Stage 0; move Stage 1 |
| `MIGRATION_PLAN.md` | **Preserve/Refactor** | `docs/MIGRATION_PLAN.md` after Stage 1 documentation move | Controls file disposition and sequencing; update only when an approved decision changes the plan. | Stage outcomes and decisions | Created Stage 0; move Stage 1; maintain throughout |

### 3.4 Dependency and tool configuration

| Existing file | Action | Final location | Reason | Dependencies | Migration order |
|---|---|---|---|---|---|
| `requirements.txt` | **Replace** | `backend/requirements.txt`; optional constrained extras such as `backend/requirements-dwave.txt` | Current file lists future backend libraries but cannot run the current app. Final backend dependencies must be validated and pinned; optional D-Wave dependencies should not burden default Aer setup. | Backend skeleton and clean install validation | Stage 1 creates backend manifest; pin Stage 17 |
| `pyproject.toml` | **Refactor** | Root `pyproject.toml` for shared Python tooling, or `backend/pyproject.toml` if backend becomes independently packaged | Keep Ruff/pytest/mypy settings, point paths at real code/tests, add strictness incrementally, and avoid dead configuration. | Backend structure and test paths | Stages 1-2; harden Stage 17 |
| `package-lock.json` | **Replace** | `frontend/package-lock.json` generated by npm from `frontend/package.json` | Existing lock is empty and has no package manifest. Generate only when Stage 1 creates the frontend; do not hand-maintain it. | `frontend/package.json`, selected supported Next.js version | Stage 1 |
| `.gitignore` | **Refactor** | `.gitignore` | Preserve existing rules, ignore root/generated caches during transition, and add frontend/backend build/test/runtime artifacts without hiding source fixtures. | Final directory layout | Stage 1, review Stage 18 |
| `docker-compose.yml` | **Refactor** | `docker-compose.yml` | Keep intended two-service topology but make it buildable only after real Dockerfiles and health behavior exist. | Backend/frontend Dockerfiles and environment files | Stage 18 |
| `backend.env.example` | **Refactor** | `backend/.env.example` | Move next to backend, validate settings through Pydantic, document bounds, and retain blank secrets. | Backend settings module | Stages 1-2 and 14 |
| `frontend.env.local.example` | **Refactor** | `frontend/.env.local.example` | Move next to frontend and retain only public service URLs. | Frontend API/WebSocket client | Stages 1 and 15 |

### 3.5 Generated cache artifacts

| Existing file/artifact | Action | Final location | Reason | Dependencies | Migration order |
|---|---|---|---|---|---|
| `cache/Fort_Kochi_India_medium.pkl` | **Deprecate** | No source location; runtime caches under ignored `backend/cache/` | Opaque version-sensitive pickle generated from external data. Do not treat it as a fixture or trusted distributable. | New cache provider and optional OSM integration test policy | Ignore in Stage 1; remove only with explicit cleanup approval after Stage 3 |
| `cache/*.json` | **Deprecate** | No source location; optional ignored `backend/cache/osmnx/` | Generated Nominatim/Overpass HTTP responses, including empty responses; not application source. | OSMnx cache configuration | Ignore in Stage 1; remove only with explicit cleanup approval after Stage 3 |

## 4. Final Repository Structure

The structure below is the intended end state. Exact module names may be adjusted only when implementation evidence requires it and the decision is recorded in `DECISIONS.md`.

```text
.
├── AGENTS.md
├── README.md
├── TASKS.md
├── pyproject.toml
├── docker-compose.yml
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── simulation/page.tsx
│   │   ├── quantum-lab/page.tsx
│   │   ├── emergency/page.tsx
│   │   ├── events/page.tsx
│   │   ├── analytics/page.tsx
│   │   └── settings/page.tsx
│   ├── components/
│   │   ├── layout/
│   │   ├── network/
│   │   ├── simulation/
│   │   ├── optimization/
│   │   ├── emergency/
│   │   ├── analytics/
│   │   └── ui/
│   ├── hooks/
│   │   ├── useSimulationSocket.ts
│   │   └── useSimulationCommands.ts
│   ├── lib/
│   │   ├── api/
│   │   ├── map/
│   │   ├── state/
│   │   └── formatting/
│   ├── types/
│   ├── public/
│   ├── tests/
│   ├── package.json
│   ├── package-lock.json
│   ├── tsconfig.json
│   ├── next.config.ts
│   ├── eslint.config.mjs
│   ├── .env.local.example
│   └── Dockerfile
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── router.py
│   │   │   └── routes/
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── errors.py
│   │   │   └── logging.py
│   │   ├── domain/
│   │   │   ├── network.py
│   │   │   ├── vehicles.py
│   │   │   ├── signals.py
│   │   │   ├── events.py
│   │   │   ├── emergency.py
│   │   │   ├── metrics.py
│   │   │   └── optimization.py
│   │   ├── routing/
│   │   │   ├── demo_network.py
│   │   │   ├── normalization.py
│   │   │   ├── routes.py
│   │   │   ├── cache.py
│   │   │   └── providers/osm.py
│   │   ├── simulation/
│   │   │   ├── engine.py
│   │   │   ├── demand.py
│   │   │   ├── movement.py
│   │   │   └── state.py
│   │   ├── signals/
│   │   │   ├── phases.py
│   │   │   ├── safety.py
│   │   │   └── controllers/
│   │   ├── optimization/
│   │   │   ├── routing/
│   │   │   │   ├── qubo.py
│   │   │   │   ├── decomposition.py
│   │   │   │   ├── decoder.py
│   │   │   │   └── service.py
│   │   │   ├── signals/
│   │   │   │   ├── qubo.py
│   │   │   │   ├── decoder.py
│   │   │   │   └── feasibility.py
│   │   │   ├── solvers/
│   │   │   │   ├── protocol.py
│   │   │   │   ├── qaoa_aer.py
│   │   │   │   ├── classical.py
│   │   │   │   └── dwave.py
│   │   │   └── hybrid.py
│   │   ├── services/
│   │   │   ├── scenario.py
│   │   │   ├── simulation.py
│   │   │   ├── optimization.py
│   │   │   ├── emergency.py
│   │   │   ├── events.py
│   │   │   └── experiments.py
│   │   ├── emergency/
│   │   │   ├── routing.py
│   │   │   ├── corridor.py
│   │   │   └── restoration.py
│   │   ├── events/
│   │   ├── metrics/
│   │   │   ├── traffic.py
│   │   │   ├── environment.py
│   │   │   └── routing.py
│   │   ├── experiments/
│   │   │   ├── runner.py
│   │   │   ├── comparison.py
│   │   │   └── export.py
│   │   └── ws/
│   │       ├── manager.py
│   │       └── events.py
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   ├── api/
│   │   ├── regression/
│   │   └── fixtures/
│   ├── requirements.txt
│   ├── requirements-dwave.txt
│   ├── .env.example
│   └── Dockerfile
│
├── docs/
│   ├── README.md
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   ├── TECH_STACK.md
│   ├── API.md
│   ├── DATA_MODEL.md
│   ├── QUANTUM_SPEC.md
│   ├── SIMULATION_SPEC.md
│   ├── UI_SPEC.md
│   ├── TESTING.md
│   ├── SECURITY.md
│   ├── DEPLOYMENT.md
│   ├── DECISIONS.md
│   ├── MIGRATION_RUNBOOK.md
│   ├── REPOSITORY_AUDIT.md
│   ├── MIGRATION_PLAN.md
│   ├── review/
│   └── archive/
│
└── legacy/
    └── streamlit/              # temporary only; removed after verified migration
```

### Frontend boundary

The frontend owns rendering, user interactions, connection state, charts, map/network presentation, and typed API/WebSocket clients. It must not import Python, calculate QUBOs, run Qiskit, or become the authority for simulation/signal safety.

### Backend boundary

The backend owns validated commands and state, simulation ticks, graph/routing, signal safety, QUBO construction, QAOA/classical/D-Wave adapters, emergency restoration, metrics, experiments, exports, and live event publication. Domain modules must remain independent of FastAPI route handlers.

### Documentation boundary

`docs/` owns product, architecture, contracts, scientific interpretation, testing, security, deployment, decisions, audits, and historical material. Root `README.md`, `AGENTS.md`, and active `TASKS.md` remain discovery/governance entry points.

## 5. Migration Order and Gates

This sequence follows `TASKS.md`; later stages must not bypass earlier gates.

| Order | Stage | Migration work | Required evidence before continuing |
|---:|---|---|---|
| 0 | Repository audit | Approve `REPOSITORY_AUDIT.md` and this plan | Reuse/deprecation decisions accepted; no implementation changed |
| 1 | Skeleton and docs | Create `frontend/`, `backend/`, `docs/`; preserve legacy files; correct manifests/readmes | Frontend starts; backend health responds |
| 2 | Domain extraction | Add typed models/settings/service interfaces; add characterization fixtures for existing records | Domain unit tests pass |
| 3 | Network/routing | Extract OSM provider and candidate routing; add deterministic six-node network; validate common graph contract | Offline and OSM modes produce the same contract |
| 4 | Simulation | Convert old demand generation and add deterministic tick/movement/queue engine | Seeded 60-second simulation test passes |
| 5 | Signals | Add phases, safety transitions, fixed baseline, controller protocol | Vehicles obey red/green and transition timing |
| 6 | Metrics | Add traffic and transparent environmental estimates | Repeated seeded baseline metrics match |
| 7 | Route MTF | Characterize and split `priority_aware_mtf.py`; add sample feasibility and explicit solver results | Old intended route behavior has regression tests; deviations documented |
| 8 | Signal QUBO | Implement separate signal variables/objective/constraints/decode | Synthetic traffic state produces a legal signal plan |
| 9 | QAOA Aer | Add Qiskit Aer adapter and metadata | Known small QUBO is solved and independently validated |
| 10 | Hybrid optimization | Connect state -> QUBO -> solver -> candidates -> validator -> classical scorer | One legal plan, with explicit fallback status, is returned |
| 11 | Adaptive simulation | Run optimization by interval and apply safe plans | 300-second run has no illegal transitions |
| 12 | Events | Add congestion, accident, closure, emergency arrival | Each event has tested state effects and lifecycle |
| 13 | Emergency corridor | Add mission route, signal priorities, conflict safety, tracking, restoration | Emergency arrives and prior controller resumes |
| 14 | FastAPI/WebSocket | Implement versioned REST and live event contracts | Commands/state/optimization work through API tests |
| 15 | Next.js UI | Replace Streamlit presentation with all specified pages/components | Pages render live typed backend state and visible failure/fallback status |
| 16 | Experiments/export | Run matched baseline/hybrid simulations and export JSON/CSV | Identical scenario inputs verified; comparison export generated |
| 17 | Hardening | Complete tests, Ruff, mypy, TypeScript, lint, build, resource bounds | All documented quality commands pass without weakened tests |
| 18 | Deployment | Add working Dockerfiles/compose and verified deployment docs | Clean integrated build starts successfully |
| 19 | Demo verification | Execute full judge flow and verify safety/quantum-honesty labels | Normal -> event -> QAOA -> emergency -> restoration -> analytics succeeds |

## 6. Dependency Order

The critical dependency chain is:

```text
Domain contracts
  -> deterministic network
  -> traffic simulation
  -> signal safety/controllers
  -> metrics
  -> route-QUBO migration
  -> signal QUBO
  -> QAOA and classical fallback
  -> hybrid application
  -> events and emergency restoration
  -> REST/WebSocket contracts
  -> Next.js UI
  -> matched experiments
  -> deployment and legacy removal
```

The frontend may be scaffolded in Stage 1, but feature UI must depend on stable typed contracts rather than inventing a separate state model. QAOA must depend on a validated QUBO and decoder, not the other way around. Emergency signal priority must depend on safe signal transitions and restoration snapshots.

## 7. Preservation and Regression Strategy

Before refactoring each existing algorithm, create small deterministic fixtures for:

- candidate routes and edge travel times;
- vehicle emergency assignment under a fixed seed;
- route variable names and expected QUBO coefficients;
- emergency/regular decomposition order;
- sample decoding and infeasible samples;
- congestion/travel-time updates;
- Dijkstra and greedy selected routes;
- route-time metric calculations;
- solver fallback identity.

Characterization tests should distinguish accidental behavior from intended behavior. Any necessary behavior correction—especially green-corridor interaction, invalid fallback routes, one-hot feasibility, or iteration congestion reset—must be recorded in `DECISIONS.md` with before/after evidence rather than hidden inside a file move.

## 8. Deprecation Exit Criteria

Do not delete or archive the Streamlit implementation until all of the following are true:

1. Existing OSM/candidate-route and route-QUBO behavior has regression coverage.
2. FastAPI exposes equivalent scenario, routing, optimization, metrics, and benchmark capabilities where those capabilities remain valid.
3. Next.js renders the required route/network and analytics information.
4. The complete PRD judge flow passes through the new applications.
5. Fallback and quantum execution labels are verified.
6. Documentation and start commands describe the actual repository state.

Do not remove legacy QUBO/solver references until the Stage 7 route migration gate passes. Do not remove generated root cache files without explicit cleanup approval; simply stop relying on them and ensure future caches are ignored.

## 9. Migration Risks and Controls

| Risk | Control |
|---|---|
| Refactor changes MTF behavior invisibly | Characterization tests, fixed fixtures, coefficient comparisons, decision log |
| Existing green-corridor claim is not reproduced | Treat it as a hypothesis; validate route interactions separately from the new signal corridor |
| Signal QUBO is conflated with route QUBO | Separate packages, variables, decoders, feasibility rules, and result types |
| QAOA failure is presented as quantum success | Mandatory solver/fallback fields and amber frontend fallback state |
| Baseline/hybrid comparison is unfair | Clone scenario state and use identical seed, demand, events, and duration |
| OSM/network dependence breaks demo | Mandatory deterministic offline six-intersection provider |
| Unsafe signal transition reaches UI/application | Backend safety state machine and feasibility validator remain authoritative |
| Pickle cache creates compatibility/security issues | Ignore generated cache, trust only locally produced cache, version or replace format |
| Frontend duplicates backend rules | Typed contracts; UI displays state but does not own simulation or safety logic |
| Legacy app is removed too early | Enforce deprecation exit criteria and Stage 19 gate |

## 10. Completion Definition

Migration is complete only when the final Next.js/FastAPI applications satisfy the PRD acceptance criteria, automated quality gates pass, the full demo flow is verified, solver identity and fallbacks are honest, and the old Streamlit implementation can be removed without losing validated functionality. This Stage 0 plan stops before any of that implementation begins.
