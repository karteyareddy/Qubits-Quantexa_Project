# Tech Stack

## Frontend

- Node.js 20+
- Next.js 15+ (use the currently supported version selected by the team)
- React
- TypeScript
- Tailwind CSS
- shadcn/ui
- Lucide React
- Framer Motion
- Recharts
- React Flow
- MapLibre GL JS OR Leaflet

Use npm unless the existing repository/team standardizes on another package manager.

## Backend

- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic
- WebSockets
- NumPy
- Pandas
- NetworkX
- OSMnx
- Qiskit
- Qiskit Aer
- dimod / existing D-Wave packages where existing solver compatibility requires them
- pytest
- pytest-cov
- ruff
- mypy

## Why

Next.js provides a production-style React UI and reusable component architecture. FastAPI provides a clean Python boundary to Qiskit and the existing traffic algorithms. WebSockets make live simulation possible.

## Dependency rule

Pin versions after a clean install is validated. Do not upgrade the entire dependency graph during feature development unless required.
