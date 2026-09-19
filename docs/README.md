# Project Migration Status

## Purpose

Stages 1 and 2 establish the target monorepo boundaries and typed backend contracts while preserving the original Streamlit application and its traffic-routing algorithms as migration references.

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
- Minimal backend and frontend dependency manifests, with backend development tools separated.
- Container definitions for the two application skeletons.

## Stage 2 status

Stage 2 complete: typed domain contracts exist; simulation, routing, signals, and optimization implementations are still pending.

## Intentionally not implemented

The current application does not implement traffic simulation, traffic-signal control, route or signal QUBOs in the new backend, QAOA, D-Wave integration, emergency green corridors, dynamic-event handling, metric formulas, benchmarking, maps, charts, WebSockets, or the final dashboard.

The root Streamlit files and `legacy/` directory remain unchanged and available as migration references. Later stages must pass their documented gates before adding these capabilities.
