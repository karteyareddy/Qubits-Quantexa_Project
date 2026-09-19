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

## 2026-09-19 — Stage 3 routing normalization

- Follow the Stage 3 topology's seven explicit bidirectional road pairs, represented as 14 directed edges.
- Preserve directed and parallel OSM edges in the domain model instead of converting them to an undirected graph.
- For node-path search only, choose the fastest open parallel edge per direction with edge ID as a deterministic tie-breaker.
- Preserve the legacy congestion multiplier but standardize domain travel time to seconds.
- Raise an explicit routing error when no path exists; never fabricate `[origin, destination]`.
- Cache only validated JSON domain models. Do not load legacy pickle caches in the new backend.

## 2026-09-19 — Stage 4 simulation model

- Use a custom one-second discrete-time engine with no external simulator dependency.
- Reuse the Stage 2 `Vehicle` and Stage 3 `Network`/`Route` contracts.
- Treat edge capacity as maximum simultaneous vehicle occupancy, rounded down to an integer with a minimum of one.
- Derive queues from vehicles blocked from entering their next edge; do not fabricate queue values.
- Process vehicles by stable ID and use local seeded random generators for reproducibility.
- Keep intersection admission behind `IntersectionEntryPolicy`; Stage 4 permits all intersections after capacity and closure checks.
- Represent emergency identity and priority metadata without implementing emergency signal priority.
