# Repository Audit

## 1. Scope and Method

This audit covers the entire checked-out repository as of 2026-09-19. It reviews all project instructions, active Python modules, legacy solver modules, documentation, configuration, dependency manifests, generated cache artifacts, and the Git file inventory. No implementation code was changed and the existing application was not migrated or deleted.

The repository currently has user-supplied migration documentation and configuration changes in the working tree in addition to the original implementation snapshot. This audit therefore distinguishes:

- the **current implementation**, which is the root-level Streamlit/Python application;
- the **target documentation**, which specifies Next.js, FastAPI, Qiskit Aer/QAOA, WebSockets, and a dynamic signal simulation; and
- the **original committed dependency documentation**, which still describes the packages needed by the Streamlit application but has been replaced in the working tree by a future-backend requirements list.

No `frontend/`, `backend/`, automated test directory, Dockerfile, or FastAPI/Qiskit implementation exists yet.

## 2. Executive Summary

The current repository is a single-process Streamlit demonstration for selecting routes on an OSMnx/NetworkX road graph. It generates a static set of regular and emergency vehicles, gives each vehicle candidate routes, formulates route-choice QUBOs, solves decomposed subproblems with local or optional D-Wave samplers, and displays routes and benchmark summaries.

The current system does **not** simulate vehicle movement over time, control traffic signals, create a signal-level green corridor, run QAOA on Qiskit Aer, expose an API, stream WebSocket state, calculate fuel/CO2, process dynamic events, or provide a Next.js interface. The existing “green corridor” is a route-allocation concept: shared route edges can receive higher QUBO penalties when emergency and regular vehicles are optimized together. It is not a sequence of safe signal priorities.

The most reusable code and ideas are:

- OSMnx loading, graph preparation, caching, and NetworkX candidate-route generation;
- the vehicle/route input shape and emergency priority metadata;
- route-choice QUBO variable mapping and normalized route-cost term;
- emergency-first decomposition and congestion-feedback concepts;
- local/D-Wave solver adapter patterns;
- classical route baselines and metric naming;
- map route styling and benchmark presentation requirements.

These assets require regression characterization and refactoring. They should not be copied unchanged into the final architecture because domain logic, solver dispatch, fallback behavior, presentation, and mutable graph state are currently coupled and untyped.

## 3. Current Architecture

```text
Streamlit app.py
  |
  +-- network_builder.py
  |     OSMnx geocoding/download or cached pickle/demo grid
  |     -> undirected NetworkX graph
  |     -> synthetic edge congestion/travel_time
  |     -> random OD pairs
  |     -> k shortest candidate routes
  |
  +-- traffic_simulator.py
  |     OD pairs -> static vehicle dictionaries
  |     -> emergency labels/weights
  |     -> candidate-route attachment
  |
  +-- priority_aware_mtf.py
  |     vehicles/routes -> decomposed route-choice QUBOs
  |     -> dimod BQM -> local or D-Wave sampler
  |     -> selected routes -> graph congestion mutation
  |     -> static route-time metrics and comparisons
  |
  +-- visualization.py
        graph/routes -> Folium map

legacy/
  priority_logic.py   reference-only route ranking/corridor edges
  qubo_builder.py     reference-only earlier route QUBO
  solver.py           reference-only solver dispatcher
```

All active orchestration and UI execution occur at import time in `app.py`. There is no application/service boundary, API contract implementation, domain model package, persistent runtime engine, or frontend/backend separation.

## 4. Important Existing Files

### 4.1 Active implementation

| File | Current responsibility | Status and significance |
|---|---|---|
| `app.py` | Streamlit page, session state, scenario creation, address geocoding, user route optimization, Folium embedding, and benchmark charts | Active entry point. It combines presentation, orchestration, external I/O, state, and benchmark execution. Preserve behavior as migration reference; do not retain it as the final UI. |
| `network_builder.py` | OSMnx graph acquisition, pickle caching, fallback grid, edge normalization, synthetic congestion, travel-time calculation, OD generation, candidate routes, and cache utilities | Active and substantially reusable after separation into graph providers, normalization, routing, scenario generation, and cache adapters. |
| `traffic_simulator.py` | Creates static vehicle dictionaries, assigns emergency subtypes/priority weights and candidate routes, identifies high-congestion edges, and assembles a scenario dictionary | Active but misnamed: it is a scenario/demand generator, not a time-stepped traffic simulator. Useful input semantics should be preserved. |
| `priority_aware_mtf.py` | Builds route-selection QUBOs, decomposes vehicles, dispatches solvers, decodes samples, mutates congestion, calculates route metrics, and compares four methods | Active optimization core and primary migration asset. It requires decomposition into focused modules and regression tests before behavioral changes. |
| `visualization.py` | Produces a static Folium map with regular, emergency, original, and optimized route styling and markers | Active presentation code. Visual semantics are reusable; Python/Folium rendering is not part of the final Next.js architecture. |

### 4.2 Legacy implementation

| File | Current responsibility | Status and significance |
|---|---|---|
| `legacy/priority_logic.py` | Separates vehicle types, scores routes against congested edges, selects preferred routes, and identifies all uncongested candidate edges as possible emergency-corridor edges | Explicitly reference-only and not imported by active code. Some rules can inform regression fixtures; its “corridor” does not select one mission route or control signals. |
| `legacy/qubo_builder.py` | Earlier variable creation and route-overlap QUBO construction using inverse priority penalties | Explicitly superseded. Retain temporarily as historical reference, then archive/deprecate after active MTF regression coverage exists. |
| `legacy/solver.py` | Standalone adapters for Neal, dimod SA, tabu, exact, direct D-Wave QPU, and Leap Hybrid plus route decoding | Explicitly reference-only. Its adapter boundaries are useful, but fallback metadata is absent and much logic duplicates `priority_aware_mtf.py`. |

### 4.3 Project and migration documentation

| File | Purpose and current state |
|---|---|
| `AGENTS.md` | Governs staged migration, architecture, quality, quantum honesty, and stop conditions. |
| `PRD.md` | Product source of truth for the final hybrid traffic-signal application and acceptance criteria. |
| `TASKS.md` | Defines Stages 0-19 and mandatory gates. The repository is currently at Stage 0. |
| `ARCHITECTURE.md` | Defines the Next.js -> FastAPI -> Python service/domain structure and live, optimization, and emergency flows. |
| `TECH_STACK.md` | Defines final frontend/backend/quantum packages and Python 3.11+/Node 20+ expectations. |
| `QUANTUM_SPEC.md` | Correctly separates existing route QUBO concepts from the required signal-control QUBO and QAOA path. |
| `SIMULATION_SPEC.md` | Defines the missing discrete simulation, six-intersection network, signal phases, events, and metrics. |
| `UI_SPEC.md` | Defines the future Next.js operations-center UI, pages, components, state, and failure UX. |
| `API.md` | Draft REST/WebSocket contract; no endpoints or WebSocket server currently implement it. |
| `DATABASE.md` | Draft runtime entity model and optional SQLite scope; no corresponding models currently exist. |
| `DECISIONS.md` | Records Next.js, FastAPI, preservation, Aer default, and offline-demo decisions. |
| `DEPLOYMENT.md` | Describes future local, environment, container, and production operation; referenced application directories do not exist yet. |
| `TESTING.md` | Defines future unit/integration/API/frontend/E2E test coverage and quality commands. None are implemented. |
| `SECURITY.md` | Defines secret handling, validation, resource bounds, CORS, untrusted OSM data, and safety messaging. Current code does not enforce these controls. |
| `DOCUMENTATION_MAP.md` | Index of project documents, including this audit and the migration plan. |
| `MIGRATION_RUNBOOK.md` | Operator sequence for executing each migration stage after review of Stage 0 outputs. |
| `CODEX_FIRST_PROMPT.md` | Earlier instruction prompt matching the present audit task. |
| `GEMINI_ROLE.md` | Defines a future review-only role and evidence format. |
| `SKILLS.md` | Lists expected engineering practices for archaeology, migration, APIs, quantum, simulation, and experiments. |
| `doc.txt` | Informal explanatory note about the old system. It overstates some “quantum-ready” and green-corridor conclusions and should not be used as scientific evidence. |
| `README.md` | Currently describes the future Next.js/FastAPI application and commands, although those directories do not exist. The committed predecessor README documented the current Streamlit application in detail. |

### 4.4 Configuration, manifests, and generated data

| File/artifact | Current state |
|---|---|
| `requirements.txt` | Contains future backend packages (`fastapi`, `pydantic`, `qiskit`, etc.) but omits packages required by the current active app (`streamlit`, `streamlit-folium`, `folium`, `dimod`, `matplotlib`, `neal`). It is unpinned. |
| `pyproject.toml` | Configures Ruff, pytest, and mypy for the future backend. `testpaths = ["backend/tests"]` points to a directory that does not exist. There is no build-system/project metadata and no strict mypy configuration. |
| `package-lock.json` | Empty npm lock structure with no `package.json` and no frontend dependencies. It does not represent an installable frontend. |
| `docker-compose.yml` | Future two-service composition referencing missing `backend/` and `frontend/` build contexts and missing Dockerfiles. It cannot build the current repository. |
| `backend.env.example` | Future backend settings including CORS, seeds, tick/optimization intervals, QAOA limits, optional OSM/D-Wave flags, and a blank token. |
| `frontend.env.local.example` | Future public API and WebSocket URLs. Contains no secret. |
| `.gitignore` | Current migration-oriented ignore list. It ignores `backend/cache/` but not the existing root `cache/`, so generated OSM files currently appear untracked. |
| `cache/Fort_Kochi_India_medium.pkl` | Pickled NetworkX/OSMnx graph generated by the current loader. Pickle is opaque, version-sensitive, and unsafe to load from untrusted sources. No cache schema/version is recorded. |
| `cache/*.json` | OSMnx HTTP cache entries: Nominatim geocoding responses, Overpass API graph responses, and empty result arrays. They are generated external-data artifacts, not source data. |

## 5. Current Data Flow

### 5.1 Startup and scenario flow

1. Importing `app.py` configures Streamlit and seeds Python and NumPy globally with `42`.
2. On first page load, `build_network_pipeline()` geocodes a place, loads/downloads an OSM graph or creates a fallback grid, converts it to an undirected graph, adds edge attributes and random congestion, computes travel times, generates random OD pairs, and finds 3-4 candidate routes per OD pair.
3. `build_traffic_scenario()` converts OD pairs into vehicle dictionaries, marks a random subset as emergency vehicles, attaches candidate routes, and reports edges above a congestion threshold.
4. `app.py` initially chooses candidate route zero for every displayed vehicle and stores graph/vehicle/route objects in Streamlit session state.
5. `visualization.py` converts these routes to Folium polylines for a static map.

### 5.2 User-route optimization flow

1. The sidebar geocodes free-text origin and destination through OSMnx/Nominatim, with broad exception handling and geographic fallbacks.
2. Coordinates are snapped to graph nodes and NetworkX calculates a `travel_time` shortest path.
3. The app generates up to five candidate routes and appends a synthetic `type="user"` vehicle.
4. `priority_aware_mtf_solve()` decomposes and solves route-choice QUBOs.
5. The selected user route is displayed as the optimized route.
6. If the optimizer returns the original route, `app.py` deliberately replaces it with the first different candidate. This means the displayed “optimized” route may not be the solver output and may be worse; this behavior must not survive migration.

### 5.3 Benchmark flow

The benchmark tab runs Dijkstra, greedy priority-first, standardized route QUBO, and priority-aware MTF against the same static vehicle/graph objects. It reports static route travel-time sums, routes selected, wall-clock solve time, percentage changes, and MTF subproblem energies. It does not run equal-duration traffic simulations or compare queues, throughput, emergency mission completion, fuel, or CO2.

## 6. Current Traffic Simulation

`traffic_simulator.py` does not implement traffic dynamics. It performs four setup operations only:

- creates one vehicle record per OD pair;
- forces at least one emergency vehicle with `max(1, int(count * emergency_ratio))`;
- gives emergency vehicles weight 10 and a random ambulance/fire/police subtype;
- attaches precomputed candidate routes and identifies graph edges whose random congestion is at least 7.

There are no simulation ticks, vehicle positions, speeds, edge occupancy/capacity enforcement, queues, arrivals, waiting/stopped time, rerouting, traffic signals, controller state, event schedule, throughput, or runtime lifecycle. “Run Simulation” in the UI rebuilds a random static scenario.

Important behavioral issues include:

- an emergency ratio of zero still creates one emergency vehicle;
- empty OD input fails during emergency sampling;
- there is no input validation or deterministic seed owned by the scenario;
- congestion is independently randomized per edge and does not arise from vehicle flow;
- the returned scenario uses mutable dictionaries and a mutable graph with no typed contract.

## 7. Current Routing and Network System

`network_builder.py` provides the current routing pipeline:

- geocodes a place and prefers `ox.graph_from_point()` with radius presets of 500/1500/3000 m;
- falls back to `ox.graph_from_place()`, then to a 5x5 NetworkX grid;
- converts the OSM graph to `nx.Graph`, discarding road direction and potentially collapsing parallel-edge semantics;
- caches the graph as a relative-path pickle under `cache/`;
- fills missing length/speed, applies random integer congestion 1-10, and computes `travel_time` in minutes using `base_time * (1 + congestion/20)`;
- generates random connected OD pairs;
- uses `nx.shortest_simple_paths(..., weight="travel_time")` for candidate routes;
- falls back to shortest path and finally `[origin, destination]`, even when that pair is not an edge.

Reusable aspects are the provider fallback concept, edge normalization, common `travel_time` weight, OD generation, bounded candidate count, and NetworkX routing. Required corrections include preserving directed/multiedge road semantics or explicitly normalizing them, introducing graph contracts and validation, removing invalid direct-path fallbacks, making seed/cache configuration explicit, and making the required 2x3 offline network deterministic.

The fallback grid lacks OSM-style `x`/`y` coordinates and CRS metadata, so the current Folium visualization path is not guaranteed to work after an OSM failure. The `fast_mode` argument is accepted and printed but does not affect behavior. Cache creation occurs at module import and is relative to the process working directory.

## 8. Current Route-Selection QUBO

### 8.1 Variables

For every vehicle `v` and candidate route index `r`, the active model creates a binary variable named `x_<vehicle_id>_<route_index>`. A selected bit means that vehicle takes that candidate route.

### 8.2 Objective terms

`build_cost_hamiltonian()` implements:

```text
H = alpha * route_cost + beta * overlap_congestion + gamma * one_route_penalty
```

- **One-route term:** negative linear bias rewards selecting a route; pairwise positive bias penalizes selecting multiple routes.
- **Route-cost term:** sums edge `travel_time` (or length), normalizes against the largest candidate cost, and multiplies emergency route cost by the vehicle priority.
- **Overlap term:** candidate routes are converted to normalized undirected edges. Shared regular/regular edges receive `beta`, emergency/emergency edges receive `2 * beta`, and emergency/regular edges receive `emergency_boost * beta`.

The dictionary is converted to `dimod.BinaryQuadraticModel.from_qubo()`.

### 8.3 Decomposition and feedback

- All emergency vehicles form the first subproblem, regardless of the configured maximum size.
- Regular vehicles are chunked in input order by `max_subproblem_size`.
- Each subproblem is solved, decoded, and its selected routes increment edge congestion on a deep-copied graph.
- Edge travel times are recalculated after assignments.
- The entire sequence repeats for three iterations by default, with congestion accumulating across iterations.

### 8.4 Correctness and interpretation risks

- This is a **route-choice QUBO**, not the signal-control QUBO required by `QUANTUM_SPEC.md`.
- Emergency and regular vehicles are intentionally placed in different subproblems. Therefore, the strong emergency/regular overlap penalty described as the green-corridor mechanism is normally never present in the same BQM. Later regular groups see only modest graph travel-time feedback from earlier emergency assignments.
- The one-route requirement is a soft penalty. There is no post-solve feasibility validator or repair step; zero or multiple selected bits are possible. Multiple selections overwrite one another during decode.
- Constraint strength is not derived from objective bounds, so feasibility is not guaranteed for all inputs.
- Candidate routes with missing edges receive a penalty in `_compute_route_cost()`, but route metrics silently skip missing edges, creating inconsistent scoring.
- Repeating iterations accumulates congestion from previous iterations as if every prior assignment remains present; there is no explicit convergence or reset rule.
- The active solver returns only a sample, so backend identity, fallback use, energy, timing, and failure causes are not represented in a typed result.
- Global Python/NumPy seeding does not necessarily seed every sampler. Benchmark repeatability is therefore not established.

These findings require regression tests and model validation before the algorithm can be claimed equivalent after refactoring. They do not justify discarding the concepts or silently changing behavior.

## 9. Current Emergency Vehicle Logic

Emergency behavior currently consists of:

- random designation of vehicle records as `type="emergency"`;
- random subtype (`ambulance`, `fire_truck`, or `police`);
- `priority_weight=10` rather than 1;
- emergency-first decomposition;
- stronger preference for low-cost routes through weighted positive route cost;
- route-overlap penalties intended to move regular routes away from emergency routes;
- green route styling on the map;
- emergency route-time metrics.

The legacy priority module can identify all non-congested edges appearing in all emergency candidate routes, but it does not choose a single corridor. The active application does not invoke this function.

There is no emergency request lifecycle, origin/destination mission object, priority vehicle movement, signal preemption, phase conflict handling, corridor intersection sequence, restoration of previous control, closed-road validation, ETA, or arrival tracking. The phrase “green corridor” in the current application means route separation, not synchronized green traffic signals.

## 10. Current Solver Architecture

The active `solve_subproblem()` supports:

| Method | Actual behavior |
|---|---|
| `neal` | Uses `neal.SimulatedAnnealingSampler` if importable; otherwise dimod simulated annealing. |
| `sa` | Uses dimod simulated annealing through the default branch. |
| `tabu` | Uses `tabu.TabuSampler` if importable; otherwise dimod simulated annealing. |
| `exact` | Uses `dimod.ExactSolver`; exponential and suitable only for very small BQMs. |

The Streamlit UI exposes only Neal, basic SA, and Leap Hybrid. The standalone legacy solver exposes the same six conceptual adapters but is not imported.

There is no Qiskit, Qiskit Aer, QAOA, QUBO-to-Ising conversion, parameter optimizer, shot/sample metadata, candidate-bitstring ranking, feasibility validation, explicit classical fallback status, or solver resource bound. Silent fallback violates the target requirement that fallback results be labeled `CLASSICAL FALLBACK` and never represented as quantum output.

No repository evidence confirms successful D-Wave QPU execution. The default and benchmark paths are classical simulated annealing and must be described as such.

## 11. Current Benchmarking

`priority_aware_mtf.py` implements:

- `dijkstra_baseline()`: independent shortest path by current graph travel time;
- `greedy_priority_baseline()`: emergency-first sequential route choice with congestion updates;
- “standard QUBO MTF”: sets all priorities to 1 and the emergency boost to 1;
- “priority-aware MTF”: retains emergency weights and uses boost 10;
- two-method and four-method comparison functions;
- static route-time metrics, routed counts, aggregate latency, solver wall time, and recorded subproblem energy.

The Streamlit benchmark visualizes method-level metrics, solve times, and energy by iteration.

Limitations relative to scientific and PRD requirements:

- methods do not run a dynamic simulation;
- the metrics are sums of per-route graph weights, not observed trip/wait/queue metrics;
- no throughput, maximum/average queue, event response, fuel estimate, CO2 estimate, or completed emergency mission time is measured;
- sampler seeds are not explicitly controlled;
- returned infeasible samples can reduce the routed count without penalty in averages;
- route fallback behavior can create nonexistent edges and zero metric contributions;
- the UI can present positive improvements without uncertainty, repeated trials, or feasibility context;
- no results are persisted or exported;
- no automated tests verify fair identical inputs or metric formulas.

The baseline algorithms and comparison schema are reusable, but Stage 16 must execute baseline and hybrid controllers against cloned scenario inputs, identical seed/demand/events/duration, and validated outputs.

## 12. Current Streamlit UI and Visualization

`app.py` provides:

- city/area input;
- time-of-day presets that alter default vehicle count and emergency ratio;
- sliders for vehicle count and emergency ratio;
- route solver selection;
- static scenario rebuild;
- address geocoding and shortest route display;
- user-route QUBO optimization;
- Folium map tab;
- four-method benchmark tab with Matplotlib charts.

State is kept in `st.session_state`, including the full mutable graph. The app avoids storing a Folium map and recreates it for rendering. Map semantics are blue regular routes, green emergency routes, red dashed original route, and orange optimized route.

Problems to address during migration:

- UI, network calls, domain orchestration, solver execution, and plotting are in one module;
- expensive geocoding can occur during Streamlit reruns;
- broad/bare exception handling hides failure categories;
- the “optimized route” can be replaced with a non-solver alternative solely to make it look different;
- initial map routes remain candidate zero and are not replaced by a full optimized assignment;
- there is no live simulation or connection/error state model;
- the app has no safety banner required by the PRD;
- mojibake is visible in the checked-out text for emoji and punctuation under the current decoding/display path;
- Python-generated Folium/Matplotlib presentation cannot be reused directly in the final Next.js UI.

The route colors, legends, metric groupings, solver status concepts, and map requirements should be translated into typed frontend components after backend contracts are stable.

## 13. Dependencies

### 13.1 Dependencies used by current active code

- `streamlit`
- `streamlit-folium`
- `osmnx`
- `networkx`
- `matplotlib`
- `numpy`
- `folium`
- `dimod`
- optional `neal` (`neal` import)
- optional `tabu` (`tabu` import)

The original committed `requirements.txt` listed these packages (plus `scikit-learn`) with lower bounds. The currently checked-out `requirements.txt` no longer lists most of them, so it cannot install the current application.

### 13.2 Declared future dependencies not yet used

- FastAPI, Uvicorn, Pydantic, python-dotenv
- Pandas
- Qiskit and Qiskit Aer
- pytest, pytest-cov, Ruff, mypy

There is no frontend package manifest. The empty npm lock does not declare Next.js, React, TypeScript, Tailwind, shadcn/ui, Lucide, Framer Motion, React Flow, Recharts, MapLibre, or Leaflet.

### 13.3 Dependency risks

- all current future Python requirements are unpinned;
- old and new runtime requirements are conflated rather than separated during migration;
- optional D-Wave dependencies and feature flags are not represented consistently;
- pickle/OSMnx cache compatibility can break across Python, NetworkX, GeoPandas, Shapely, or OSMnx versions;
- the target Docker composition has no build files yet.

## 14. Existing Tests and Verification

There are no test files in the repository, no `tests/` directory, no CI workflow, and no recorded test fixtures. `pyproject.toml` points pytest at the nonexistent `backend/tests` directory. There are no frontend, API, WebSocket, simulation, QUBO, solver, route, metric, or regression tests.

`network_builder.py` has a manual `__main__` smoke path that downloads/builds a graph and prints counts. It is not an automated test and depends on external state unless cache or fallback behavior intervenes.

This Stage 0 task did not run/install the application because the user explicitly restricted work to inspection and the current requirements manifest does not describe the active Streamlit runtime. Before migration changes behavior, characterization tests are required for route generation, QUBO coefficients, decomposition, decoding, congestion updates, baselines, and metrics.

## 15. Reusable Code and Concepts

### Preserve with regression tests

- route-choice variable semantics `(vehicle_id, route_index)`;
- normalized route travel-cost calculation;
- emergency priority metadata and emergency-first scheduling intent;
- candidate-route generation with NetworkX;
- OSMnx provider and offline fallback concept;
- travel-time edge normalization and congestion feedback concept;
- classical Dijkstra and greedy comparison methods;
- exact/local/D-Wave adapter concepts;
- metric result naming where it remains semantically accurate;
- route visualization color and legend semantics.

### Refactor before reuse

- mutable dictionaries into typed Pydantic/domain models;
- one monolithic MTF module into formulation, decomposition, solver, decode/validate, metrics, and benchmark modules;
- graph download/cache into provider interfaces;
- random global state into scenario-owned seeded generators;
- static vehicle generation into demand generation feeding a real simulator;
- silent solver fallback into explicit typed solver outcomes;
- Streamlit orchestration into backend services and API commands;
- Folium/Matplotlib rendering into frontend data contracts and React visualizations.

### Preserve only as historical reference

- legacy priority, QUBO, and solver modules after regression tests cover relevant behavior;
- Streamlit UI until the Next.js migration is verified;
- old explanatory claims only where they can be supported by tests and honest solver metadata.

## 16. Technical Problems and Debt

### Critical correctness and honesty

1. Displayed optimized user routes can be substituted with an arbitrary different candidate rather than the solver result.
2. Quantum/D-Wave failures silently become classical simulated annealing without returned fallback metadata.
3. The active “green corridor” penalty is structurally weakened by separating emergency and regular vehicles into different QUBO subproblems.
4. Samples are not checked for one-route feasibility before decode/use.
5. Documentation and UI language can imply stronger quantum execution and corridor behavior than the code proves.

### Architecture and maintainability

1. No typed domain models, service boundaries, dependency injection, or API layer.
2. Root-level mutable graph and dictionary contracts are shared across modules.
3. Solver logic is duplicated between active and legacy modules.
4. UI and orchestration are coupled in import-time Streamlit code.
5. Broad exception handling and print statements replace structured errors/logging.
6. No automated tests, CI, lint baseline, type hints throughout, or documentation tied to implemented state.

### Simulation and routing

1. No actual traffic simulation or signals.
2. OSM directed/multigraph semantics are discarded.
3. Invalid direct routes can be fabricated on routing failure.
4. Demo network lacks the coordinates/metadata expected by visualization and does not match the required six-intersection topology.
5. Randomness is global and partially controlled; benchmark samplers are not explicitly seeded.
6. Iterative congestion accumulation has no reset/convergence semantics.
7. Relative pickle cache is unversioned and unsafe if obtained from an untrusted source.

### Configuration and operability

1. Current requirements cannot run the current Streamlit app.
2. README/start commands describe missing future applications.
3. Compose references missing directories and Dockerfiles.
4. Package lock has no package manifest or dependencies.
5. Root cache is not ignored by the current `.gitignore`.
6. No runtime validation or resource bounds exist for graph size, vehicles, BQM size, reads, or remote calls.

## 17. Missing Functionality Relative to `PRD.md`

| PRD area | Current state | Missing work |
|---|---|---|
| Final architecture | Root Streamlit monolith | Next.js frontend, FastAPI backend, typed REST/WebSocket boundary, service/domain layers |
| Offline network | Random 5x5 fallback | Deterministic seeded 2x3 six-intersection graph with 12 bidirectional links and common network contract |
| Dynamic simulation | Static demand records | Tick engine, movement, capacity, queues, wait/stopped time, arrivals, rerouting, lifecycle |
| Signals | None | NS/EW phases, yellow/all-red, min/max green, legal transitions, fixed/adaptive controllers |
| Signal QUBO | None | `x(i,p,d)` variables, normalized objective terms, constraints, decoder, feasibility validator |
| QAOA | None | Qiskit Aer execution, Ising conversion, reps/shots/optimizer, samples, metadata, explicit fallback |
| Emergency corridor | Route priority only | Mission route, intersection sequence, safe temporary signal plan, conflicts, tracking, restoration |
| Dynamic events | None | Congestion, accident, closure, emergency-arrival events with duration and state effects |
| Environmental estimates | None | Transparent fuel and CO2 estimate formulas/configuration/labels |
| Live updates | None | WebSocket event stream and normalized client state |
| Explainability | QUBO energies and summary metrics only | Variables, objective breakdown, backend, QAOA parameters, bitstring, feasibility, decoded plan, runtime/fallback |
| Benchmark integrity | Static route comparison | Matched baseline/hybrid dynamic runs with identical seed, demand, events, duration, and complete metrics |
| Export/history | None | JSON/CSV export and optional experiment history |
| UI pages | Two Streamlit tabs | Dashboard, Simulation, Quantum Lab, Emergency, Events, Analytics, Settings |
| Safety/security | Documentation only | Visible safety banner, Pydantic validation, CORS, resource bounds, secret isolation, safe errors |
| Testing | None | Domain, simulation, routing, optimization, API, frontend, integration, and optional E2E suites |
| Deployment | Spec-only compose | Working Dockerfiles, validated local commands, integrated build |

## 18. Audit Conclusion

The repository contains a useful route-optimization prototype, not an early version of the complete target product. Migration should begin by characterizing and extracting existing behavior, then building the deterministic traffic/signal domain around it. The existing route QUBO should remain a distinct optimization capability and emergency-routing input; it must not be relabeled as signal optimization. Streamlit and legacy files should remain in place until equivalent backend behavior and the Next.js presentation are verified at their respective gates.
