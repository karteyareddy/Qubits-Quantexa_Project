# Quantum Traffic Optimizer — Next.js Edition

Hybrid quantum-classical adaptive urban traffic optimization.

## Architecture

Next.js -> FastAPI -> Python simulation/optimization -> Qiskit Aer / NetworkX

## Start backend

```bash
cd backend
python -m venv .venv
# activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Start frontend

```bash
cd frontend
npm install
npm run dev
```

Open:
`http://localhost:3000`

## Documentation

Start with:
- AGENTS.md
- PRD.md
- TASKS.md

## Demo

1. Start 6-intersection scenario.
2. Start simulation.
3. Trigger congestion.
4. Run QAOA.
5. Apply optimized signals.
6. Start ambulance mission.
7. Show green corridor.
8. Show restoration.
9. Compare metrics.
10. Export.

This is a simulation/research prototype and must not control real traffic infrastructure.
