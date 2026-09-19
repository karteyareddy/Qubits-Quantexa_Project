# Emergency Green Corridor Subsystem (Stage 13)

## 1. Overview

The Emergency Green Corridor subsystem implements time-aware signal preemption and green-wave progression for active emergency vehicles. When an emergency vehicle enters the simulation, the service predicts intersection arrival times, reserves green signal windows along the route, and overrides normal adaptive schedules to grant uninterrupted right-of-way.

```text
Emergency Vehicle
       ↓
Route Extraction & Rerouting
       ↓
Signalized Intersections
       ↓
ETA Prediction
       ↓
Green Windows Calculation
       ↓
Safe Signal Priority (Preemption)
       ↓
Emergency Passage
       ↓
Corridor Release & Adaptive Control Resumption
```

> [!IMPORTANT]
> **This is a prototype emergency signal-priority mechanism, not a production-certified emergency traffic-control system.**

---

## 2. Subsystem Architecture

```text
backend/app/emergency/
├── models.py      Typed domain models (EmergencyCorridor, CorridorIntersectionReservation, EmergencyCorridorConfig)
├── route.py       EmergencyRouteExtractor (route validation, intersection sequence, dynamic rerouting)
├── predictor.py   EmergencyETAPredictor (arrival ETA prediction, green window bounds, phase mapping)
├── corridor.py    EmergencyCorridorPlanner (validated corridor building)
├── controller.py  EmergencyCorridorController (signal preemption overrides over adaptive control)
└── service.py     EmergencyCorridorService (lifecycle management, release, rerouting checks)
```

---

## 3. Detailed Component Mechanisms

### A. Route Extraction & Intersection Sequencing (`route.py`)
- Extracts the emergency vehicle's active route.
- Identifies ordered signalized intersections (`I1 → I2 → I3 → ...`) along the route while preserving travel movement direction.
- If a road closure blocks an edge on the active route, invokes Stage 3 `generate_candidate_routes` to dynamically reroute from the vehicle's current location to its destination.

### B. ETA & Green-Window Calculation (`predictor.py`)
- Calculates deterministic arrival time (ETA) at each intersection using remaining edge length, free-flow speed, position on edge, and edge congestion multiplier.
- Constructs green window bounds:
  $$\text{window\_start} = \max(\text{current\_time}, \text{ETA} - \text{arrival\_buffer})$$
  $$\text{window\_end} = \text{ETA} + \text{clearance\_buffer}$$
- Maps incoming approach axis (`NORTH_SOUTH` or `EAST_WEST`) to corresponding Stage 5 green phases (`NS_GREEN` or `EW_GREEN`).

### C. Signal Priority Preemption (`controller.py`)
- Overrides active `AdaptiveSignalPolicy` phases for intersections with active green window reservations.
- Maintains conflict safety: non-corridor approach movements remain protected by standard signal indication rules (no simultaneous green on conflicting axes).

### D. Corridor Lifecycle & Clean Release (`service.py`)
- **PLANNED**: Corridor created with intersection reservations.
- **ACTIVE**: Signal preemption overrides active during green windows.
- **COMPLETED**: Emergency vehicle reaches destination (`VehicleState.ARRIVED`); preemption is released immediately, and Stage 11 adaptive control resumes.
- **CANCELLED / FAILED**: Route blocked without valid alternate route; recorded with explicit failure reason.

---

## 4. Interaction with Other Subsystems

1. **Stage 11 (Adaptive Control)**: Active emergency green windows take precedence over QAOA/hybrid signal schedules. Once the corridor completes, adaptive control resumes seamlessly.
2. **Stage 12 (Dynamic Events)**: Triggered by `EmergencyArrivalEvent`. Responds to `RoadClosureEvent` by dynamic rerouting.
3. **Stage 6 (Metrics)**: Tracks emergency vehicle travel time, waiting time, and corridor duration in `ScenarioMetrics`.

---

## 5. Limitations

1. **Single-Corridor Preemption Priority**: Concurrent emergency vehicle requests queue deterministically; multi-agent corridor negotiation is deferred to future work.
2. **Deterministic ETA Estimation**: ETAs use deterministic discrete simulation kinematics rather than stochastic ML traffic forecasting.
