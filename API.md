# API Contract

## Implementation status

Stage 3 adds internal network providers and candidate routing, but no routing endpoint. `GET /health` remains the only implemented HTTP endpoint. The scenario, simulation, optimization, event, emergency, metrics, export, and WebSocket sections below are future contracts and are not yet available.

Base URL:
`http://localhost:8000/api/v1`

## Health

`GET /health`

Response:
```json
{"status":"ok"}
```

## Scenarios

`GET /scenarios`

`POST /scenarios/load`

Request:
```json
{"scenario_id":"demo_6_intersection","seed":42}
```

## Simulation

`POST /simulation/start`

`POST /simulation/pause`

`POST /simulation/reset`

`POST /simulation/step`

Request:
```json
{"seconds":5}
```

`GET /simulation/state`

## Optimization

`POST /optimization/run`

Request:
```json
{
  "controller":"hybrid_quantum",
  "qaoa_reps":1,
  "shots":256
}
```

`GET /optimization/{run_id}`

## Events

`POST /events`

```json
{
  "type":"congestion",
  "target":"E5",
  "severity":0.8,
  "duration_seconds":60
}
```

Types:
- congestion
- accident
- road_closure
- emergency_arrival

## Emergency

`POST /emergency`

```json
{
  "origin":"I1",
  "destination":"I6",
  "vehicle_type":"ambulance"
}
```

`POST /emergency/{mission_id}/restore`

## Metrics

`GET /metrics/current`

`GET /experiments/{experiment_id}`

`POST /experiments/run`

## Export

`GET /experiments/{experiment_id}/export?format=csv`

## WebSocket

`WS /ws/simulation`

Event envelope:
```json
{
  "type":"simulation_tick",
  "timestamp":120,
  "payload":{}
}
```

Event types:
- connected
- simulation_tick
- event_started
- event_ended
- optimization_started
- qubo_created
- quantum_progress
- optimization_completed
- optimization_failed
- signal_plan_applied
- emergency_started
- emergency_updated
- emergency_completed
- metrics_updated
- error
