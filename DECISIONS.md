# Decisions

## 2026-09-19 — Next.js frontend
Use Next.js + TypeScript instead of Streamlit for the final UI.

Reason:
- richer component ecosystem
- live WebSocket UI
- better visual control
- clean separation from Python quantum backend.

## 2026-09-19 — FastAPI backend
Use FastAPI as the boundary between Next.js and Python simulation/quantum services.

## 2026-09-19 — Preserve existing repository
The existing Priority-Aware MTF/QUBO/routing implementation is valuable and must be refactored rather than discarded.

## 2026-09-19 — Qiskit Aer default
Use Qiskit Aer for the default QAOA demonstration so the core project does not require paid quantum hardware.

## 2026-09-19 — Offline demo mode
Provide a deterministic six-intersection network independent of live OSM data.
