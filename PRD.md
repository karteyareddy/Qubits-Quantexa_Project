# PRD — Quantum-Enhanced Adaptive Urban Traffic Optimization
## Next.js + FastAPI Edition

## 1. Source of truth

This product is based on:
1. The supplied hackathon problem statement.
2. The existing GitHub repository `Joann-jk/Quantum-Traffic-Priority-Routing`.

The existing repository already provides a Priority-Aware MTF/QUBO traffic-routing foundation, emergency-vehicle prioritization, iterative decomposition, congestion feedback, OSMnx/NetworkX routing, multiple solver backends, benchmarking, and a Streamlit/Folium UI. Preserve useful logic; do not rebuild equivalent functionality unnecessarily.

The supplied problem statement additionally requires a hybrid quantum-classical platform for 4–8 connected intersections, QUBO/QAOA or hybrid optimization, adaptive traffic signals, emergency green corridors, dynamic events, environmental estimates, classical comparison, and an interactive dashboard.

## 2. Final architecture decision

The final product MUST use:

### Frontend
- Next.js
- TypeScript
- React
- Tailwind CSS
- shadcn/ui
- Lucide icons
- Framer Motion
- React Flow for network visualization where useful
- Recharts for analytics
- MapLibre GL JS or Leaflet for geographic visualization

### Backend
- Python
- FastAPI
- Pydantic
- Uvicorn
- WebSockets

### Quantum
- Qiskit
- Qiskit Aer
- QAOA
- Existing D-Wave integrations may remain as optional solver adapters, but are not required for the default demo.

### Simulation/routing
- NetworkX
- Existing traffic simulator logic, refactored into backend domain services
- Existing OSMnx integration as optional real-world mode
- Deterministic 6-intersection demo network as mandatory offline mode

### Data
- In-memory runtime state for the demo
- JSON/CSV experiment exports
- SQLite optional for experiment history
- No database is required for MVP

## 3. Product goal

Build a visually polished web application that simulates an interconnected urban traffic network, dynamically optimizes traffic signals using a hybrid quantum-classical workflow, creates emergency green corridors, responds to dynamic events, and compares results with a classical baseline.

## 4. Required user experience

A judge must be able to:
1. Open the Next.js dashboard.
2. Start a deterministic 6-intersection simulation.
3. Watch traffic/queues/signals update live.
4. Trigger congestion.
5. Run QAOA optimization.
6. See the QUBO and quantum solver status.
7. Apply the optimized signal plan.
8. Inject an emergency vehicle.
9. See its route and green corridor.
10. See restoration after the emergency passes.
11. Compare baseline and hybrid metrics.
12. Export results.

## 5. Core features

### F1 — Multi-intersection network
- Support 4–8 intersections.
- Default: 6.
- Show density, queue, road capacity, signal state.
- Represent the network as a graph.

### F2 — Traffic simulation
- Discrete simulation tick, default 5 seconds.
- Deterministic seed.
- Vehicle generation.
- Route assignment.
- Position/speed/waiting state.
- Queue formation.
- Throughput tracking.

### F3 — Traffic signals
- NS/EW phase model at minimum.
- Green/yellow/all-red.
- Minimum and maximum green.
- Safe transitions.
- Fixed baseline controller.
- Adaptive optimized controller.

### F4 — Existing Priority-Aware MTF preservation
Preserve and refactor useful existing concepts:
- Priority-aware route QUBO.
- Emergency boost.
- Iterative decomposition.
- Congestion feedback.
- Candidate route generation.
- Existing classical/D-Wave solver adapters where practical.

Do not force the existing route-only QUBO to pretend it is signal optimization. Introduce a clean signal-decision QUBO and allow route priority to influence the joint objective.

### F5 — QUBO
Decision variables represent discrete signal-control choices over a short horizon.
Objective includes:
- waiting
- queue
- congestion
- throughput
- emergency travel time
- fuel estimate
- CO2 estimate
- transition penalties
- legality constraints

### F6 — QAOA
Default execution:
- Qiskit Aer local simulator.
- Configurable reps and shots.
- Classical optimizer for QAOA parameters.
- Candidate bitstrings decoded and feasibility-checked.

If QAOA fails, use an explicit classical fallback and display `CLASSICAL FALLBACK`. Never label fallback output as quantum.

### F7 — Emergency Green Corridor
- Emergency origin/destination.
- NetworkX route.
- Intersections on route.
- Temporary signal priority.
- Conflict handling.
- Emergency tracking.
- Restoration of previous control.

### F8 — Dynamic events
Support:
- congestion
- accident
- road closure
- emergency arrival

### F9 — Environmental estimates
Compute transparent estimates for:
- fuel
- CO2

Label them as estimates.

### F10 — Benchmarking
Run baseline and hybrid on identical:
- network
- seed
- demand
- event schedule
- duration

Compare:
- average wait
- total wait
- queue
- throughput
- emergency travel time
- fuel
- CO2

### F11 — Live UI
WebSocket-powered live state updates.

### F12 — Explainability
Show:
- traffic state
- QUBO variables
- objective terms
- solver
- QAOA parameters
- bitstring
- feasibility
- signal plan
- runtime
- fallback status

## 6. Pages

### Dashboard
Overview, live KPIs, network, current controller.

### Simulation
Detailed live simulation controls and network.

### Quantum Lab
QUBO matrix, objective breakdown, QAOA details, result.

### Emergency
Emergency mission, route, corridor, signal priority, restoration.

### Events
Trigger and configure events.

### Analytics
Baseline-vs-hybrid charts and experiment results.

### Settings
Scenario, seed, simulation parameters, optimization parameters.

## 7. Non-goals
- Real traffic signal control.
- Safety-critical deployment.
- Claiming universal quantum advantage.
- Paid quantum hardware as a requirement.
- Mandatory live OSM data.

## 8. Default scenario
- 6 intersections, 2x3 grid.
- 12 bidirectional road links.
- 5-second tick.
- 30-second optimization interval.
- 300-second demo.
- Seed 42.
- Congestion event around simulated second 60.
- Optional road closure around second 120.
- One emergency mission.

## 9. Acceptance criteria
The application must run locally with:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

cd ../frontend
npm install
npm run dev
```

Then:
- frontend loads,
- backend health works,
- WebSocket connects,
- simulation starts,
- state updates live,
- QAOA can run locally,
- emergency corridor works,
- analytics render,
- export works,
- automated tests pass.

## 10. Safety
Display:
`Simulation/research prototype — not for controlling real traffic infrastructure.`
