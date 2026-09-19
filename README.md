# Quantum-Enhanced Adaptive Urban Traffic Optimization

An end-to-end platform combining deterministic traffic micro-simulation, Signal-Control QUBO formulations, Qiskit Aer QAOA quantum circuit optimization, dynamic event injection, emergency green corridors, and a Next.js interactive dashboard.

---

## 1. System Architecture

```text
Next.js 16 Dashboard (Port 3000)
       │ (HTTP REST / WebSocket Live Stream)
       ▼
FastAPI REST & WebSocket API (Port 8000)
       │
       ├── Traffic Simulation Engine & Domain Network
       ├── Adaptive Signal Controller & Scheduler
       ├── Dynamic Traffic Event Engine (Accidents, Closures, Spikes)
       ├── Emergency Green Corridor Service (ETA & Signal Preemption)
       └── Hybrid Quantum-Classical Optimizer
               ├── Signal-Control QUBO Builder
               ├── Qiskit / Aer QAOA Circuit Solver
               └── Classical Heuristic / Brute-Force Fallback
```

---

## 2. Requirements

- **Python**: `3.11` or higher
- **Node.js**: `20.x` LTS or higher
- **npm**: `10.x` or higher
- **Docker & Docker Compose**: (Optional)

---

## 3. Quickstart & Local Setup

### 1. Install Dependencies

```bash
make install
# Or manually:
python -m pip install -r requirements.txt
cd frontend && npm ci
```

### 2. Start Services

```bash
# Terminal 1: Backend API (:8000)
make backend
# Or manually: python -m uvicorn app.api.main:app --reload --port 8000

# Terminal 2: Frontend UI (:3000)
make frontend
# Or manually: cd frontend && npm run dev
```

Open `http://localhost:3000` in your browser.

---

## 4. Environment Configuration

Copy environment templates:

```bash
cp .env.example .env
cp backend.env.example backend/.env
cp frontend.env.local.example frontend/.env.local
```

Key environment variables:
- `CORS_ORIGINS`: Allowed origins (default: `http://localhost:3000`)
- `RANDOM_SEED`: Deterministic simulation seed (default: `42`)
- `QAOA_REPS`: Circuit layers $p$ (default: `1`)
- `MAX_QAOA_QUBITS`: Aer qubit safety threshold (default: `30`)
- `NEXT_PUBLIC_API_URL`: Backend REST URL (default: `http://localhost:8000`)
- `NEXT_PUBLIC_WS_URL`: WebSocket URL (default: `ws://localhost:8000/api/v1/simulations`)

---

## 5. Docker Deployment

Run complete stack in containerized environment:

```bash
# Build and start container stack
make docker-up
# Or: docker compose up -d --build

# Teardown container stack
make docker-down
# Or: docker compose down
```

---

## 6. Testing & Quality Gates

Run complete test suite, linter, type checker, and automated deployment smoke test:

```bash
# Run pytest backend test suite
make test

# Run Ruff linter, Mypy type check, and ESLint
make lint

# Run frontend production build
make build

# Run end-to-end automated deployment smoke test
make smoke
```

---

## 7. Demonstration Workflow (Judge Flow)

1. **Start Simulation**: Select scenario (`low-traffic` or `congested-traffic`) and start simulation.
2. **Observe Baseline**: View live vehicle movements and traffic metrics.
3. **Inject Event**: Inject dynamic event (e.g. `Congestion Spike` or `Road Closure`).
4. **Trigger QAOA Optimization**: Execute hybrid quantum-classical optimization and review QAOA depth, energy, and solver fallback reporting.
5. **Request Emergency Green Corridor**: Trigger ambulance mission (`I1` $\rightarrow$ `I6`) and observe real-time signal preemption and green windows.
6. **Compare Benchmarks**: View side-by-side QAOA vs. Classical Fixed-Time baseline metrics.

---

## 8. Documentation Index

- [`PRD.md`](file:///c:/Users/karte/Documents/Quantexa/Quantum-Traffic-Priority-Routing-main/PRD.md) — Product requirements and final architecture
- [`TASKS.md`](file:///c:/Users/karte/Documents/Quantexa/Quantum-Traffic-Priority-Routing-main/TASKS.md) — Stage execution roadmap and status
- [`docs/DEPLOYMENT.md`](file:///c:/Users/karte/Documents/Quantexa/Quantum-Traffic-Priority-Routing-main/docs/DEPLOYMENT.md) — Comprehensive deployment guide
- [`docs/HARDENING.md`](file:///c:/Users/karte/Documents/Quantexa/Quantum-Traffic-Priority-Routing-main/docs/HARDENING.md) — Platform hardening & resource limits
- [`docs/DETERMINISM.md`](file:///c:/Users/karte/Documents/Quantexa/Quantum-Traffic-Priority-Routing-main/docs/DETERMINISM.md) — Seed propagation & state reproducibility
- [`docs/BENCHMARK.md`](file:///c:/Users/karte/Documents/Quantexa/Quantum-Traffic-Priority-Routing-main/docs/BENCHMARK.md) — Controlled benchmark methodology & results
- [`docs/API.md`](file:///c:/Users/karte/Documents/Quantexa/Quantum-Traffic-Priority-Routing-main/docs/API.md) — REST & WebSocket API specification
- [`docs/FRONTEND.md`](file:///c:/Users/karte/Documents/Quantexa/Quantum-Traffic-Priority-Routing-main/docs/FRONTEND.md) — Next.js UI dashboard architecture
- [`DOCUMENTATION_MAP.md`](file:///c:/Users/karte/Documents/Quantexa/Quantum-Traffic-Priority-Routing-main/DOCUMENTATION_MAP.md) — Complete documentation map

---

> [!NOTE]
> This platform is a research prototype designed for hackathon demonstration and simulation evaluation.
