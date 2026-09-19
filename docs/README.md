# Project Migration Status

## Purpose

Stages 1 through 3 establish the target monorepo boundaries, typed backend contracts, and independent network/routing layer while preserving the original Streamlit application and its algorithms as migration references.

```text
frontend/  Next.js and TypeScript presentation layer
backend/   FastAPI and Python application boundary
docs/      Migration and implementation documentation
```

## Run the backend

From the repository root:

```bash
cd backend
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

The Stage 1 backend exposes one endpoint:

```text
GET http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```

## Run the frontend

From the repository root in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

Validation commands:

```bash
npm run lint
npm run build
```

## Currently implemented

- Minimal FastAPI application and health endpoint.
- Minimal Next.js/React/TypeScript homepage.
- Target package directories for future staged work.
- Validated network, route, vehicle, signal, event, emergency, metrics, scenario, and optimization contracts.
- Environment-backed backend settings and a typed domain/service error hierarchy.
- Protocols for future scenario, simulation, optimization, emergency, event, and experiment services.
- Unit tests for Stage 2 models, settings, serialization, and solver/fallback metadata.
- Fully offline deterministic six-intersection demo network with 14 directed edges.
- Optional OSMnx provider normalized to the same `Network` domain contract.
- Directed/parallel-edge-preserving NetworkX normalization and deterministic candidate routes.
- Validated JSON network cache with configurable location and no pickle loading.
- Deterministic discrete-time traffic simulation with scheduled arrivals, movement, capacity, queues, completion, and serializable snapshots.
- Low-traffic, congested, emergency-vehicle, and locally seeded demand scenarios.
- Network-derived approaches, deterministic fixed-time signal controllers, safe phase transitions, and serializable signal snapshots.
- Signal-aware simulation blocking for red/yellow indications while preserving downstream capacity checks.
- Deterministic traffic, queue, per-vehicle, emergency, edge, and intersection-approach outcome metrics.
- Configurable prototype fuel and CO2 estimates with explicit non-calibrated labeling.
- Minimal backend and frontend dependency manifests, with backend development tools separated.
- Container definitions for the two application skeletons.

## Stage 2 status

Stage 2 complete: typed domain contracts exist; simulation, routing, signals, and optimization implementations are still pending.

## Stage 3 status

Stage 3 complete: offline and optional OSM network providers, normalization, caching, validation, and candidate routing exist. Traffic simulation, vehicle movement, signal control, QUBO/QAOA, emergency corridors, dynamic events, and routing APIs remain pending.

## Stage 4 status

Stage 4 complete: the offline simulation engine models routed vehicle arrivals, edge movement, capacity blocking, emergent queues, waiting, completion, and emergency identity. See `TRAFFIC_SIMULATION.md`. Signal control, formal metrics, events, optimization, APIs, and live publication remain pending.

## Stage 5 status

Stage 5 complete: deterministic fixed-time controllers derive approaches from the Stage 3 network and control Stage 4 intersection entry. See `TRAFFIC_SIGNALS.md`. Adaptive control, formal metrics, signal optimization, events, APIs, and live publication remain pending.

## Stage 6 status

Stage 6 complete: controller-independent scenario metrics cover completion, throughput, waiting, travel, queues, per-vehicle and emergency outcomes, plus explicitly labeled prototype fuel and CO2 estimates. See `TRAFFIC_METRICS.md`. Optimization, events, experiments, APIs, and live publication remain pending.

OSM mode is optional and installed separately:

```bash
cd backend
python -m pip install -r requirements-osm.txt
```

## Intentionally not implemented

The current application does not implement adaptive traffic-signal control, route or signal QUBOs in the new backend, QAOA, D-Wave integration, emergency green corridors, dynamic-event handling, benchmarking, routing REST endpoints, maps, charts, WebSockets, or the final dashboard.

The root Streamlit files and `legacy/` directory remain unchanged and available as migration references. Later stages must pass their documented gates before adding these capabilities.
