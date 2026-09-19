# Dynamic Traffic Events Subsystem (Stage 12)

## 1. Overview

The Dynamic Traffic Events subsystem provides deterministic, typed event injection for altering traffic conditions while the simulation is running. It bridges static network simulations with dynamic urban environments.

```text
Event
  ↓
Simulation State Mutation
  ↓
Traffic Observer
  ↓
Signal-Control QUBO
  ↓
QAOA / Hybrid Optimization
  ↓
Updated Signal Schedule
```

> [!IMPORTANT]
> **Stage 12 supports emergency vehicle arrival but does not yet implement an emergency green corridor.** Signal preemption for emergency vehicles is implemented in Stage 13.

---

## 2. Supported Event Types

| Event Type | Class | Target | Key Parameters | Effect |
| :--- | :--- | :--- | :--- | :--- |
| **Congestion Spike** | `CongestionSpikeEvent` | Edge | `additional_vehicle_count` | Injects additional vehicles into approach queues |
| **Accident** | `AccidentEvent` | Edge | `severity`, `capacity_factor`, `duration` | Scales effective edge capacity (`edge.capacity *= factor`) |
| **Road Closure** | `RoadClosureEvent` | Edge | `duration` | Sets `edge.closed = True`, excluding edge from candidate routes |
| **Emergency Arrival** | `EmergencyArrivalEvent` | Intersection | `vehicle_id`, `origin`, `destination`, `priority` | Injects emergency vehicle with `is_emergency=True` |

---

## 3. Event Lifecycle

```text
SCHEDULED ──> ACTIVE ──> EXPIRED / RESOLVED
    │
    └───> FAILED
```

1. **SCHEDULED**: Registered in `EventScheduler`, awaiting `simulation_time >= timestamp`.
2. **ACTIVE**: Applied to simulation state; holds temporary dynamic effects (e.g., capacity reduction or road closure) for a specified `duration`.
3. **EXPIRED**: Effect duration completed (`current_time >= expired_time`); original state restored.
4. **RESOLVED**: Instantaneous event (e.g., vehicle injection) completed successfully.
5. **FAILED**: Application encountered an unrecoverable error; recorded in event history.

---

## 4. Deterministic Scheduler & Ordering

`EventScheduler` sorts events due at the same timestamp using strict priority rules:

1. `timestamp` (ascending)
2. `event_type` priority rank:
   - `ROAD_CLOSURE` (Rank 10)
   - `ACCIDENT` (Rank 20)
   - `CONGESTION_SPIKE` (Rank 30)
   - `EMERGENCY_ARRIVAL` (Rank 40)
3. `event_id` (alphabetical tie-breaker)

This guarantees bit-for-bit reproducible event application regardless of Python runtime dictionary ordering or system architecture.

---

## 5. Subsystem Models & Behavior

### Accident Model
- Temporarily reduces `NetworkEdge.capacity` by `capacity_factor` (e.g., `0.25` = 25% capacity remaining).
- Upon event expiration, original capacity is restored.

### Road Closure Model
- Sets `NetworkEdge.closed = True`.
- Dynamic routing (`generate_candidate_routes`) collapses edges with `closed = True`, preventing new routes from taking the closed edge.
- Vehicles currently traversing a closed edge complete their traversal safely without teleportation or deletion.

### Congestion Spike Model
- Generates `additional_vehicle_count` vehicles with `arrival_time_seconds = current_time`.
- Injects vehicles directly into `pending_vehicles` to increase demand on target approaches.

### Emergency Arrival Model
- Injects a `Vehicle` with `vehicle_type = VehicleType.EMERGENCY` and `is_emergency = True`.
- Retains priority weighting (`priority_weight = priority`) for observer and QUBO weighting.

---

## 6. Failure Handling & Idempotency

- **Idempotency**: Unique `event_id` enforcement prevents duplicate event registration or double execution.
- **Fail Fast**: Configurable `fail_fast=True` raises `EventHandlerError` on event application failure; `fail_fast=False` logs `EventStatus.FAILED` in history and continues simulation.

---

## 7. Limitations

1. **No Emergency Green Corridor**: Emergency vehicles participate in queue metrics and QUBO weighting, but dedicated green corridors (signal preemption) are deferred to Stage 13.
2. **No Mid-Edge Teleportation**: Rerouting applies to new route requests; vehicles currently on a closed edge complete their traversal.
