# First Prompt for Codex

You are modifying the existing repository `Quantum-Traffic-Priority-Routing`.

Do NOT build a new unrelated project.

First read:
- AGENTS.md
- PRD.md
- TASKS.md
- ARCHITECTURE.md
- TECH_STACK.md

Then inspect the entire existing repository, especially:
- README.md
- app.py
- priority_aware_mtf.py
- traffic_simulator.py
- network_builder.py
- visualization.py
- requirements.txt
- package-lock.json
- legacy/
- all solver-related files if present

Do NOT modify implementation code yet.

Create:
1. REPOSITORY_AUDIT.md
2. MIGRATION_PLAN.md

The audit must identify:
- existing features
- reusable modules
- current dependencies
- current quantum formulation
- current emergency routing
- current simulation
- current UI
- solver backends
- tests
- technical debt

The migration plan must map:
existing file -> final backend/frontend module -> action (preserve/refactor/replace/deprecate)

Final architecture must be:
Next.js + TypeScript frontend
FastAPI + Python backend
Qiskit Aer/QAOA quantum path
NetworkX/OSMnx routing
WebSocket live updates

Do not start implementation until these two documents are complete.
