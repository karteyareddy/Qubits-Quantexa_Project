# Data Model

MVP requires no persistent database.

## Stage 2 typed contracts

The backend now defines serializable Pydantic contracts under `backend/app/domain/`:

- `Network`, `NetworkNode`, `NetworkEdge`, and `Coordinates`
- `Route` and `Vehicle`
- `SignalState`
- `TrafficEvent`
- `EmergencyMission`
- `TrafficMetrics`, `EnvironmentalMetrics`, and `EmergencyMetrics`
- `Scenario` and `ScenarioConfiguration`
- `OptimizationResult`, `SolverMetadata`, `OptimizationPlan`, and `FeasibilityResult`

These models validate identifiers, non-negative structural values, graph references, event and mission timelines, nested scenario serialization, and optimization fallback consistency. They contain no persistence, movement, routing, signal-transition, event-handling, metric-formula, or solver behavior.

## Runtime entities

### Intersection
id, position, phases, min_green, max_green, yellow, all_red.

### RoadEdge
id, source, target, length_m, capacity, speed, travel_time, closed.

### Vehicle
id, type, origin, destination, route, current_edge, position, speed, waiting_time, stopped_time, emergency.

### TrafficState
simulation_time, intersections, edges, vehicles, active_events, active_emergencies.

### SignalPlan
intersection_id, phase, green_seconds, start_time, end_time, priority.

### TrafficEvent
id, type, target, severity, start_time, end_time, metadata.

### EmergencyMission
id, origin, destination, route, current_edge, status, start_time, arrival_time, corridor_intersections.

### OptimizationResult
run_id, solver, status, variables, bitstring, objective, feasible, signal_plan, runtime_ms, fallback_used, qaoa_parameters.

The Stage 2 optimization contract additionally classifies execution as exactly `QUANTUM`, `CLASSICAL`, or `CLASSICAL FALLBACK`. A fallback result requires both an explicit fallback flag and reason.

## Optional SQLite

If persistence is added:
- scenarios
- experiments
- experiment_runs
- metric_samples
- optimization_runs

Do not add SQLite until the in-memory MVP is stable.
