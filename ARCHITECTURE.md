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

## Stage 3 routing boundary

```text
DemoNetworkProvider ----+
                        +-> Network domain contract -> candidate routes
OSMNetworkProvider -----+            |
        |                             +-> NetworkX routing graph
        +-> validated JSON cache
```

- The demo provider is offline and deterministic for an explicit seed.
- OSMnx is an optional dependency and may fall back explicitly to another provider.
- OSM direction and parallel-edge identities remain in the domain contract.
- Node-path routing collapses parallel edges only for path search, selecting the open edge with the lowest travel time and using edge ID as a deterministic tie-breaker.
- Candidate routing raises an explicit `RouteNotFoundError`; it never fabricates a direct edge.
- Routing remains an internal service with no Stage 3 REST endpoint.

## Stage 4 simulation boundary

```text
SimulationScenario + Stage 3 Network/Route
        -> TrafficSimulation
        -> capacity + intersection-entry policy
        -> SimulationState snapshots
```

- The custom engine advances in deterministic, configurable discrete timesteps.
- Vehicle state reuses the Stage 2 domain model and adds runtime timing/progress fields.
- Occupancy and queues are derived from active vehicle positions and blocked transitions.
- `IntersectionEntryPolicy` permits Stage 5 signal control without adding signal behavior now.
- The simulation package has no FastAPI, WebSocket, UI, optimizer, or quantum dependency.

## Stage 5 signal boundary

```text
Network incoming edges -> SignalApproach mapping
        -> FixedTimeSignalController per intersection
        -> SignalSystem -> FixedTimeSignalPolicy
        -> simulation IntersectionEntryPolicy
```

- Approach axes derive from network coordinates and directed incoming edges.
- Fixed cycles expose explicit green, yellow, red, and optional all-red behavior.
- Only one axis may be green; yellow and all-red deny new intersection entry.
- Signal permission is evaluated at the vehicle's exact crossing time within a simulation step.
- Timing is classical and fixed; no queue adaptation, optimization, or quantum logic exists in Stage 5.

## Stage 6 metrics boundary

```text
Simulation states -> MetricsService
        -> traffic/queue/emergency aggregation
        -> prototype environmental estimates
        -> ScenarioMetrics
        -> future evaluation and benchmarking
```

- Metrics consume simulation outcomes and never choose routes, phases, or optimizations.
- Travel outcomes use completed vehicles; waiting outcomes include all spawned vehicles.
- Historical queue metrics use explicitly supplied deterministic state observations.
- Fuel and CO2 are labeled configurable prototype estimates, not calibrated measurements.
- The result contract is controller-independent for fair future comparisons.

## Stage 7 optimization boundary

```text
Stage 3 Network & Candidate Routes + Vehicles
        -> PriorityMTFOptimizerService
        -> variables (x(v,r)) + objective + qubo
        -> solver abstraction (neal/sa/tabu/exact/qpu/dwave)
        -> decoder -> feasibility verification
        -> OptimizationResult + SolverMetadata
```

- Optimizes route-choice allocations for vehicles across candidate paths.
- Does not modify signal timing or execute signal control (belongs to Stage 8+).
- Subproblem decomposition groups emergency vehicles into subproblem 0.
- Solution decoder produces explicit feasibility results and violations.
- Solver abstraction captures fallback metadata and execution class (`CLASSICAL`, `QUANTUM`, `CLASSICAL_FALLBACK`).

## Stage 8 Signal QUBO boundary

```text
SimulationState + Network + SignalQuboConfig
        -> SignalQuboBuilder
        -> x(i, p, t) variables + H_constraint + H_traffic_surrogate
        -> Q matrix + linear/quadratic terms + constant offset
        -> evaluator / reference_solver / future QAOA (Stage 9)
        -> decode_signal_qubo_solution -> SignalSchedule
```

- Formulates binary signal timing decisions $x(i, p, t)$ over short discrete horizons $H$.
- Enforces exactly-one-phase constraint $\sum_p x(i, p, t) = 1$ via quadratic penalty $A$.
- Minimizes surrogate traffic cost: queue length, waiting pressure, emergency vehicles, throughput rewards, and switching penalties.
- Decodes binary assignments into typed `SignalSchedule` domain models.
- Formulation is solver-independent and provides exact $Q_{i, j}$ matrices for Stage 9 QAOA.

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
```

## Stage 9 QAOA Architecture
Stage 9 introduces the first actual QAOA implementation (`app.quantum`), constructing parameterized quantum circuits using Qiskit 2.5.2 and executing simulation on Qiskit Aer 0.17.2 against Stage 8 signal-control QUBOs ($x(i,p,t) \in \{0, 1\}$).
