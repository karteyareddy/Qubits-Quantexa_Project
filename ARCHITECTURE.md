# Architecture

## High-level

```text
Next.js Browser
   |
   | REST
   | WebSocket
   v
FastAPI Backend
   |
   +-- Scenario Service
   +-- Simulation Service
   +-- Signal Service
   +-- Optimization Service
   +-- Emergency Service
   +-- Event Service
   +-- Metrics Service
   |
   +--------------------+
   |                    |
   v                    v
Traffic Domain       Quantum Domain
   |                    |
NetworkX              QUBO
OSMnx optional        QAOA / Aer
Vehicles              Classical fallback
Signals               Existing D-Wave adapters
```

## Repository architecture

```text
frontend/
  app/
  components/
  hooks/
  lib/
  types/
  public/

backend/
  app/
    main.py
    api/
    core/
    domain/
    simulation/
    optimization/
    routing/
    metrics/
    services/
    ws/
  tests/

docs/
```

## Principles

1. Next.js contains UI only.
2. Python contains simulation, routing, metrics and quantum logic.
3. Frontend never imports Python code.
4. Backend never contains UI rendering logic.
5. REST is used for commands/configuration/history.
6. WebSocket is used for live simulation and optimization events.
7. Domain models are independent of FastAPI and React.
8. Existing repository algorithms are migrated/refactored, not copied into duplicate modules.
9. Deterministic demo mode is independent of internet access.
10. OSM mode remains optional.

## Stage 2 domain boundary

The first implemented backend boundary is contract-only:

```text
backend/app/domain/       validated serializable state and result models
backend/app/services/     protocols with no concrete service behavior
backend/app/core/         settings and typed service/domain errors
```

The domain package does not import FastAPI, NetworkX, OSMnx, Qiskit, or the legacy implementation. Routing providers, simulation behavior, signal controllers, optimization builders/solvers, and WebSocket publication remain assigned to later stages.

## Live flow

```text
Simulation tick
 -> SimulationService
 -> EventService
 -> SignalController
 -> MetricsService
 -> WebSocket broadcaster
 -> Next.js state store
 -> UI
```

## Optimization flow

```text
TrafficState
 -> QUBOBuilder
 -> QAOAService
 -> Candidate bitstrings
 -> Decoder
 -> FeasibilityValidator
 -> ClassicalTrafficScorer
 -> OptimizationResult
 -> WebSocket progress/result
 -> Apply SignalPlan
```

## Emergency flow

```text
Emergency request
 -> route
 -> identify intersections
 -> create corridor plan
 -> apply temporary priorities
 -> simulate
 -> arrival
 -> restore previous plans
 -> metrics
```
