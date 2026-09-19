# Platform Hardening & Reliability Specification

## Overview

Stage 17 enforces system-wide reliability, strict boundary validation, explicit failure modes, resource safeguards, and simulation invariant protection across the Quantum-Enhanced Adaptive Urban Traffic Optimization platform.

## 1. Input Boundary Validation

Every public REST, WebSocket, event, and simulation parameter input is audited and validated before entering the core engine:

- **Simulation Configuration**: Duration must be between `10.0s` and `3600.0s` (`max_simulation_duration_seconds`). Timesteps must be strictly positive.
- **Topology Verification**: Node IDs and edge IDs in event requests or routing requests must exist in the active `Network` topology. Unknown nodes/edges raise `ValidationError` (HTTP 400).
- **Dynamic Events**: Event start timestamps must be non-negative. Durations must be strictly positive.
- **API Payloads**: Payload sizes exceeding configurable maximum thresholds are rejected cleanly with structured HTTP 400 or HTTP 422 JSON errors. Stack traces are never exposed in production API responses.

## 2. Platform Resource Limits

Safety bounds prevent runaway computational workloads:

```python
class PlatformResourceLimits:
    max_simulation_duration_seconds: float = 3600.0
    max_vehicles_per_simulation: int = 500
    max_qubo_variables: int = 100
    max_qaoa_qubits: int = 30
    max_qaoa_shots: int = 10000
    max_benchmark_repetitions: int = 20
    max_event_payload_size_bytes: int = 10000
```

Requests violating these thresholds return structured `RESOURCE_LIMIT_EXCEEDED` errors.

## 3. Simulation State Invariants

The `TrafficSimulation` engine maintains strict state consistency:
- **Monotonic Time**: Simulation time `t` advances strictly forward (`t_next > t`). Backwards time movement or negative step durations are rejected.
- **Vehicle Lifecycle**: Vehicle IDs are unique. Exited/arrived vehicles transition to `WAITING` or `ARRIVED` state and cannot re-enter as active vehicles.
- **Non-negative Quantities**: Queue lengths, edge occupancies, waiting times, and travel times are strictly non-negative. Zero-vehicle scenarios do not cause division by zero.
- **Concurrency Safety**: Active `SimulationSession` instances wrap step, optimization, event injection, and emergency corridor operations in an `asyncio.Lock()` to prevent race conditions during concurrent REST/WebSocket calls.

## 4. Optimization & QAOA Truthfulness

Quantum-classical optimization metadata is explicit and transparent:
- **Fallback Transparency**: If QAOA quantum simulation fails or returns no feasible sample, the solver transparently falls back to classical heuristic/brute-force policies.
- **Truthful Metadata**: Fallback execution is NEVER labeled as quantum execution. `fallback_used=True`, `fallback_reason`, and `solver_name` ("classical_reference", "fallback_fixed_time") explicitly detail solver status.
- **Authoritative Energy**: QUBO energy evaluation uses one canonical formulation across QAOA sampling and classical reference solvers.

## 5. WebSocket & System Resiliency

- **Client Disconnect**: WebSocket handlers cleanly remove disconnected sockets from subscription sets (`ws_manager.disconnect()`) without interrupting background simulation sessions.
- **Subsystem Health Endpoint**: `GET /health` returns application status and granular subsystem availability (`subsystems` object).
