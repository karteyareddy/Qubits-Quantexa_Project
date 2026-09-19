# FastAPI REST + WebSocket API Specification

This document details the FastAPI REST and WebSocket API specification for the **Quantum-Enhanced Adaptive Urban Traffic Optimization** engine.

---

## 1. Overview & Architecture

The API layer functions as a typed adapter interfacing the Next.js frontend with the core Python simulation and quantum optimization services:

```text
Next.js Frontend
       │
       ├── REST API ─────────► FastAPI Controllers ──► Simulation / Hybrid QAOA / Events / Emergency
       │                            │
       └── WebSocket ───────────────┴───────────────► Live State Updates (Broadcaster)
```

- **Framework**: FastAPI
- **Serialization**: Pydantic v2
- **Protocol**: HTTP/1.1 (REST) & WebSockets
- **Base Path**: `/api/v1`
- **Documentation**: `/docs` (Swagger UI) & `/openapi.json`

---

## 2. Global Endpoints

### `GET /health`
Returns backend health status.

**Response `200 OK`**:
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

---

## 3. Network & Scenarios API

### `GET /api/v1/network`
Returns the deterministic 6-intersection demo network topology.

**Response `200 OK`**:
```json
{
  "intersections": [
    { "intersection_id": "I1", "name": "Intersection I1", "is_signalized": true, "position": null }
  ],
  "edges": [
    {
      "edge_id": "I1->I2",
      "source_intersection": "I1",
      "target_intersection": "I2",
      "free_flow_travel_time_seconds": 30.0,
      "capacity": 20.0,
      "length_meters": 500.0
    }
  ],
  "signalized_intersections": ["I1", "I2", "I3", "I4", "I5", "I6"]
}
```

### `GET /api/v1/scenarios`
Exposes deterministic traffic scenarios.

**Response `200 OK`**:
```json
[
  {
    "scenario_id": "low-traffic",
    "name": "Low Traffic Scenario",
    "description": "3 vehicles routed across the 6-intersection network",
    "duration_seconds": 120.0,
    "vehicle_count": 3,
    "emergency_vehicle_count": 0
  },
  {
    "scenario_id": "congested-traffic",
    "name": "Congested Traffic Scenario",
    "description": "30 vehicles departing simultaneously causing heavy queueing",
    "duration_seconds": 120.0,
    "vehicle_count": 30,
    "emergency_vehicle_count": 0
  },
  {
    "scenario_id": "emergency-vehicle",
    "name": "Emergency Priority Scenario",
    "description": "Normal vehicles plus an active Ambulance requiring green corridor",
    "duration_seconds": 120.0,
    "vehicle_count": 3,
    "emergency_vehicle_count": 1
  }
]
```

---

## 4. Simulation Session API

### `POST /api/v1/simulations`
Creates a new simulation session.

**Request Body**:
```json
{
  "scenario_id": "low-traffic",
  "duration_seconds": 120.0,
  "control_interval_seconds": 5.0,
  "seed": 42,
  "adaptive_enabled": true,
  "events_enabled": true,
  "emergency_corridor_enabled": true
}
```

**Response `201 Created`**:
```json
{
  "simulation_id": "sim-a1b2c3d4",
  "status": "created",
  "scenario_id": "low-traffic",
  "simulation_time_seconds": 0.0,
  "created_at": 1726760000.0
}
```

### `GET /api/v1/simulations/{simulation_id}`
Returns complete simulation state snapshot.

**Response `200 OK`**:
```json
{
  "simulation_id": "sim-a1b2c3d4",
  "status": "created",
  "simulation_time_seconds": 0.0,
  "vehicles": [...],
  "signals": [...],
  "edges": [...],
  "active_events": [],
  "emergency_corridors": [],
  "metrics": {...}
}
```

### `POST /api/v1/simulations/{simulation_id}/start`
Starts session running mode.

### `POST /api/v1/simulations/{simulation_id}/pause`
Pauses session execution.

### `POST /api/v1/simulations/{simulation_id}/step`
Advances simulation state by `step_seconds`.

**Request Body**:
```json
{
  "step_seconds": 1.0
}
```

### `POST /api/v1/simulations/{simulation_id}/stop`
Stops simulation and marks as completed.

---

## 5. Signal Optimization API

### `POST /api/v1/simulations/{simulation_id}/optimize`
Triggers manual hybrid quantum-classical QAOA optimization on current traffic state.

**Request Body**:
```json
{
  "solver": "hybrid",
  "apply_immediately": true
}
```

**Response `200 OK`**:
```json
{
  "simulation_id": "sim-a1b2c3d4",
  "timestamp": 15.0,
  "solver_name": "QAOA-Aer-Simulator",
  "qubo_energy": -14.5,
  "is_feasible": true,
  "selected_schedule": {
    "I1": "NS_GREEN",
    "I2": "EW_GREEN"
  },
  "optimization_time_seconds": 0.042,
  "fallback_used": false,
  "fallback_reason": null,
  "applied_to_simulation": true,
  "schedule_details": [
    { "intersection_id": "I1", "selected_phase": "NS_GREEN", "phase_duration_seconds": 30.0 }
  ],
  "raw_metrics": {}
}
```

---

## 6. Dynamic Events API

### `POST /api/v1/simulations/{simulation_id}/events`
Injects a dynamic event into the simulation.

**Request Payload Examples**:
- **Congestion Spike**: `{"type": "congestion_spike", "timestamp": 10.0, "edge_id": "I1->I2", "multiplier": 3.0, "duration": 30.0}`
- **Accident**: `{"type": "accident", "timestamp": 15.0, "edge_id": "I2->I5", "capacity_reduction": 0.5, "duration": 45.0}`
- **Road Closure**: `{"type": "road_closure", "timestamp": 20.0, "target": "I1->I4", "duration": 60.0}`
- **Emergency Arrival**: `{"type": "emergency_arrival", "timestamp": 8.0, "vehicle_id": "amb-999", "origin": "I1", "destination": "I6", "emergency_subtype": "AMBULANCE", "priority_weight": 10}`

### `GET /api/v1/simulations/{simulation_id}/events`
Lists all event records (scheduled, active, completed, expired).

---

## 7. Emergency Green Corridor API

### `GET /api/v1/simulations/{simulation_id}/emergency`
Lists active emergency corridors and green windows.

### `POST /api/v1/simulations/{simulation_id}/emergency/{vehicle_id}/activate`
Activates or rebuilds an emergency green corridor for a specific vehicle.

---

## 8. Simulation Metrics API

### `GET /api/v1/simulations/{simulation_id}/metrics`
Returns throughput, delay, travel time, waiting time, fuel, CO2, emergency corridor metrics, and optimization statistics.

---

## 9. Live WebSocket Stream

### `WS /api/v1/simulations/{simulation_id}/ws`
Establishes a WebSocket connection for live state streaming.

**Outbound Envelope**:
```json
{
  "type": "state",
  "timestamp": 10.0,
  "data": { ... }
}
```

**Inbound Client Messages**:
- Ping: `{"action": "ping"}` -> Response `{"type": "pong", "timestamp": 10.0}`
- Step: `{"action": "step", "step_seconds": 1.0}` -> Broadcasts updated `"state"` envelope.

---

## 10. Error Handling & Format

All API errors return a standard JSON structure:
```json
{
  "error": {
    "code": "SIMULATION_NOT_FOUND",
    "message": "Simulation session 'sim-123' does not exist."
  }
}
```

HTTP Status Codes:
- `400 Bad Request`: Domain rule violation or invalid input.
- `404 Not Found`: Session, vehicle, or scenario not found.
- `409 Conflict`: Invalid state transition.
- `422 Unprocessable Entity`: Optimization constraint failure.
- `500 Internal Server Error`: Unexpected internal failure.
