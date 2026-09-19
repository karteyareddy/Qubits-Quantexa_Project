# UI/UX Specification — Next.js

## Visual direction

Modern operations-center dashboard:
- dark-first theme
- high information density
- restrained animation
- strong status indicators
- responsive layout
- no Streamlit UI

Do not use excessive decorative animation. Animation must communicate state.

## Global layout

```text
Sidebar
  Dashboard
  Simulation
  Quantum Lab
  Emergency
  Events
  Analytics
  Settings

Main content
```

## Dashboard

Top KPIs:
- Avg waiting
- Max queue
- Throughput
- Emergency ETA
- Fuel estimate
- CO2 estimate

Main:
- live network visualization
- active events
- controller status
- optimization status

## Simulation page

Controls:
- Start
- Pause
- Reset
- Step
- Speed
- Controller
- Optimization interval

Network:
- intersections
- edges
- queues
- signals
- vehicles

## Quantum Lab

Show:
- QUBO variable count
- matrix visualization
- objective breakdown
- QAOA reps
- shots
- backend
- current run status
- best bitstring
- feasibility
- decoded signal plan
- runtime

## Emergency

Show:
- origin/destination
- route
- corridor intersections
- current position
- priority signal states
- elapsed time
- estimated travel time
- restoration status

## Events

Forms:
- event type
- target
- severity
- duration
- activate

## Analytics

Charts:
- waiting over time
- queue over time
- throughput
- emergency travel time
- fuel
- CO2
- baseline vs hybrid

## Components

Recommended:
- `Sidebar`
- `KpiCard`
- `NetworkCanvas`
- `IntersectionNode`
- `SignalBadge`
- `VehicleMarker`
- `EventBanner`
- `OptimizationStatus`
- `QuboHeatmap`
- `QaoaPanel`
- `EmergencyCorridor`
- `MetricChart`
- `ComparisonTable`
- `ScenarioControls`
- `ToastProvider`

## State

Use React state/hooks for local UI. Use a small client-side store only if needed. WebSocket data should have a single normalized state model.

## Error UX

- API errors -> toast + inline error
- WebSocket disconnect -> connection badge + retry
- optimization failure -> visible failed state
- fallback -> amber `CLASSICAL FALLBACK`
- never hide failures
