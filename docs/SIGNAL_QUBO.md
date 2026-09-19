# Signal-Control QUBO Formulation

## Overview

Stage 8 introduces a **Signal-Control QUBO formulation** that optimizes intersection traffic signal phase decisions across a short discrete time horizon $H$.

> **Crucial Distinction**: Stage 8 formulates **intersection signal timing decisions** $x(i, p, t)$, whereas Stage 7 optimized **vehicle route selection** $x(v, r)$. Stage 8 is solver-independent and provides the exact QUBO matrix $Q_{i, j}$ that Stage 9's QAOA quantum solver will solve.

```text
Simulation State Snapshot
        |
        v
SignalQuboBuilder (with SignalQuboConfig)
        |
        +-> variables.py: x(i, p, t) binary decision variables
        +-> objective.py: traffic surrogate cost (queue, waiting, throughput, emergency, switching)
        +-> builder.py: Q matrix, linear/quadratic terms, constant offset
        +-> evaluator.py: exact energy evaluation E(x)
        +-> decoder.py: decodes binary bitstring -> SignalSchedule
        +-> reference_solver.py: brute-force validation (< 20 variables)
```

## Decision Variable Mapping

For each intersection $i$, valid green phase $p$, and discrete time interval $t \in [0, H-1]$:

$$x(i, p, t) \in \{0, 1\}$$

Interpretation: $x(i, p, t) = 1$ means intersection $i$ selects green phase $p$ during time interval $t$.

Variables use deterministic names:
`x_{intersection_id}_P{phase_index}_T{interval_index}` (e.g. `x_I1_P0_T0`, `x_I1_P1_T0`).

## Exactly-One-Phase Constraint

For every intersection $i$ and time interval $t$, exactly one green phase must be selected:

$$\sum_{p} x(i, p, t) = 1$$

In QUBO quadratic penalty form:

$$A \cdot \left(\sum_p x(i, p, t) - 1\right)^2 = A \cdot \left( -\sum_p x(i, p, t) + 2 \sum_{p < q} x(i, p, t) x(i, q, t) \right) + A$$

* Linear terms: $-A \cdot x(i, p, t)$
* Quadratic terms: $+2A \cdot x(i, p, t) x(i, q, t)$ for $p \neq q$
* Constant offset: $+A$ per $(i, t)$

## Traffic Surrogate Cost Model

$$\text{TrafficCost}(x) = \text{QueueCost}(x) + \text{WaitingCost}(x) - \text{ThroughputReward}(x) + \text{EmergencyPenalty}(x) + \text{SwitchingCost}(x)$$

1. **Queue Penalty**: Unserved approaches add $+w_q \times q_{\text{edge}}$.
2. **Waiting Penalty**: Unserved approaches add $+w_w \times w_{\text{edge\_waiting}}$.
3. **Throughput Reward**: Served approaches credit $-w_{\text{throughput}} \times \min(q_{\text{edge}}, C)$.
4. **Emergency Priority**: Unserved emergency vehicles add $+w_{\text{emergency}} \times \text{count}_{\text{emergency}}$.
5. **Switching Penalty**:
   * Initial interval $t=0$: if $x(i, p, 0) = 1$ differs from previous phase, adds $+w_{\text{switch}}$.
   * Consecutive intervals $t, t+1$: if phase changes ($p \neq q$), quadratic penalty $+w_{\text{switch}} \cdot x(i, p, t) x(i, q, t+1)$ is added.

## Configuration Parameters

All weights and penalty terms are configurable in `SignalQuboConfig`:
* `horizon_intervals`: default 3
* `interval_seconds`: default 10.0
* `constraint_penalty` ($A$): default 100.0
* `queue_weight`: default 2.0
* `waiting_weight`: default 1.0
* `throughput_weight`: default 1.5
* `emergency_weight`: default 20.0
* `switch_weight`: default 5.0

## Energy Evaluation & Validation

Energy is evaluated exactly:

$$E(x) = \sum_{(u, v)} Q_{(u, v)} x_u x_v + \text{constant\_offset}$$

`solve_signal_qubo_brute_force` provides an exact reference solver enumerating all $2^N$ assignments for small instances ($N \le 20$), proving global ground truth for QAOA validation.

## Limitations

* Signal QUBO uses a short discrete decision horizon $H$ (surrogate traffic cost).
* Phase indications use simplified two-axis green movements (`EW_GREEN`, `NS_GREEN`).
* High-density continuous traffic dynamics are approximated per discrete interval.
