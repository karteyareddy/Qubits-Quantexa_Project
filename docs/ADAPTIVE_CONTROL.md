# Closed-Loop Adaptive Traffic Optimization (`docs/ADAPTIVE_CONTROL.md`)

## 1. Overview

This document specifies the technical design of the **Closed-Loop Adaptive Traffic Optimization Subsystem** (`app.adaptive`) introduced in **Stage 11**.

The adaptive controller closes the loop between discrete-time traffic simulation and receding-horizon quantum-classical signal optimization:

```text
Simulation Engine
       ↓
Observe Traffic (TrafficObserver)
       ↓
Build Signal-Control QUBO (Stage 8)
       ↓
Hybrid QAOA Optimization (Stage 9 + Stage 10)
       ↓
Optimized Signal Schedule (SignalSchedule)
       ↓
Apply Schedule (AdaptiveSignalPolicy)
       ↓
Advance Simulation Step
       ↓
Observe Again (Receding Horizon)
```

---

## 2. Receding-Horizon Control & Control Cadence

- Optimization triggers at explicit control boundaries $t = k \cdot \text{control\_interval\_seconds}$ (e.g. $t = 0, 10, 20, 30 \dots$).
- For each control interval, `TrafficObserver` extracts an immutable traffic state snapshot without mutating simulation engine state.
- Stage 8 `SignalQuboBuilder` constructs a state-dependent QUBO based on real-time queues, waiting times, approach occupancies, and emergency vehicles.
- Stage 10 `HybridSignalOptimizer` finds the minimum-energy feasible `SignalSchedule`.
- `AdaptiveSignalPolicy` applies the schedule to controlled intersections for the duration of the control interval.

---

## 3. Signal Safety Rules

- Optimized schedules are applied via `AdaptiveSignalPolicy` without bypassing signal controller safety rules.
- Intersections only permit vehicle entry on green phases (`EW_GREEN` or `NS_GREEN`) matching the approach movement axis.
- If optimization fails or yields no feasible solution, the controller retains the previous valid schedule or falls back to fixed-time baseline control.

---

## 4. Metrics & Event Tracking

Each adaptive simulation run returns an `AdaptiveRunResult` containing:
- Complete Stage 6 `ScenarioMetrics` (traffic outcomes, environmental estimates, emergency metrics).
- Chronological `AdaptiveOptimizationEvent` log recording timestamps, solver identities, QUBO energies, feasibility status, and optimization durations.

---

## 5. Prototype Disclaimer

> [!NOTE]
> The Stage 11 adaptive loop implements receding-horizon heuristic signal control. It provides the architectural foundation for subsequent dynamic traffic events (accidents, closures, emergency corridors) and benchmark comparisons.
