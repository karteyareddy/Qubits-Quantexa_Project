# Deployment & Production-like Packaging Guide

## Overview

This guide details the deployment architecture, environment configuration, local developer workflow, containerization, healthchecks, and demo verification procedure for the Quantum-Enhanced Adaptive Urban Traffic Optimization platform.

## Architecture & System Overview

```text
Next.js 16 Dashboard (Port 3000)
       │ (HTTP REST / WebSocket)
       ▼
FastAPI Backend (Port 8000)
       │
       ├── Traffic Simulation Engine & Domain Network
       ├── Adaptive Signal Controller & Scheduler
       ├── Dynamic Traffic Event Engine
       ├── Emergency Green Corridor Service
       └── Hybrid Quantum-Classical Optimizer
               ├── Classical Fixed-Time / Heuristic Solver
               └── QAOA Circuit Solver (Qiskit / Aer Simulator)
```

## System Requirements

- **Python**: Version 3.11 or higher
- **Node.js**: Version 20.x LTS or higher
- **npm**: Version 10.x or higher
- **Docker & Docker Compose**: (Optional, for containerized deployment)

---

## 1. Local Developer Workflow

### Installation

Install backend Python dependencies and frontend npm packages:

```bash
# Using Makefile
make install

# Manual equivalent
python -m pip install -r requirements.txt
cd frontend && npm ci
```

### Running Backend Service

Start the FastAPI application with auto-reload:

```bash
# Using Makefile
make backend

# Manual equivalent
python -m uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

- **Backend API Base**: `http://localhost:8000`
- **Swagger / OpenAPI Documentation**: `http://localhost:8000/docs`
- **Subsystem Health Endpoint**: `http://localhost:8000/health`

### Running Frontend Dashboard

Start the Next.js development server:

```bash
# Using Makefile
make frontend

# Manual equivalent
cd frontend && npm run dev
```

- **Interactive Dashboard UI**: `http://localhost:3000`

---

## 2. Docker & Containerized Deployment

Multi-stage container images are provided for production-like execution.

### Building & Running with Docker Compose

```bash
# Using Makefile
make docker-up

# Manual equivalent
docker compose up -d --build
```

### Container Healthchecks & Ports

- **Backend Container**: `quantum_traffic_backend` listening on port `8000`. Container healthcheck queries `http://localhost:8000/health` every 10s.
- **Frontend Container**: `quantum_traffic_frontend` listening on port `3000`. Starts automatically once backend reports healthy status.

### Stopping Containers

```bash
# Using Makefile
make docker-down

# Manual equivalent
docker compose down
```

---

## 3. Environment Variables Reference

Environment configuration templates are provided in `.env.example`, `backend.env.example`, and `frontend.env.local.example`.

| Variable Name | Default Value | Description |
|---|---|---|
| `APP_ENV` | `development` | Environment mode (`development` or `production`) |
| `HOST` | `0.0.0.0` | Backend bind address |
| `PORT` | `8000` | Backend bind port |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated CORS allowed origins |
| `RANDOM_SEED` | `42` | Seed for pseudo-random number generation |
| `SIM_TICK_SECONDS` | `1.0` | Simulation timestep duration in seconds |
| `OPTIMIZATION_INTERVAL_SECONDS` | `5.0` | Frequency of adaptive optimization steps |
| `MAX_SIMULATION_DURATION_SECONDS` | `3600.0` | Platform safety threshold for maximum simulation time |
| `QAOA_REPS` | `1` | Number of QAOA circuit layers ($p$) |
| `QAOA_SHOTS` | `256` | Quantum circuit sampling shot count |
| `MAX_QAOA_QUBITS` | `30` | Maximum qubit threshold supported by Aer simulator |
| `ENABLE_OSM` | `false` | Whether to query live OpenStreetMap network topology |
| `LOG_LEVEL` | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Frontend REST API target URL |
| `NEXT_PUBLIC_WS_URL` | `ws://localhost:8000/api/v1/simulations` | Frontend WebSocket target URL |

---

## 4. Automated Deployment & Smoke Testing

To verify end-to-end subsystem health, REST endpoints, QAOA execution, dynamic events, emergency corridors, metrics, and benchmark comparisons:

```bash
# Using Makefile
make smoke

# Manual equivalent
python scripts/smoke_test.py
```

---

## 5. Troubleshooting & Fallback Behavior

### Qiskit / Aer Availability
If Qiskit Aer GPU/CPU simulation is unavailable or if a QUBO problem exceeds `max_qaoa_qubits` (30 qubits), the `HybridSignalOptimizer` automatically uses classical reference heuristics. Fallback status is explicitly recorded (`fallback_used=True`) and never mislabeled as quantum advantage.

### Offline / OpenStreetMap Fallback
If `ENABLE_OSM` is `false` or live network access is unavailable, the application defaults to the canonical 6-intersection grid topology (`I1` through `I6`).

### WebSocket Resiliency
If WebSocket connection drops, client-side hooks (`useSimulationSocket`) automatically handle reconnect loops, and backend `WebSocketConnectionManager` cleanly discards dead subscriptions without crashing simulation sessions.
