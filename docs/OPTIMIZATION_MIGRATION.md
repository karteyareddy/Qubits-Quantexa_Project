# Stage 7 Optimization Migration: Priority-Aware MTF

## Scope and Purpose

Stage 7 migrates the existing `priority_aware_mtf.py` route-choice optimization algorithm into a structured backend package (`backend/app/optimization/`).

> **Architectural Note**: Stage 7 migrates the existing Priority-Aware MTF route-choice allocation optimization. It is NOT the final signal-control quantum optimization required by the project. Signal-control QUBO and QAOA belong to later stages (Stage 8+).

```text
Stage 3 Network & Routing
        |
Candidate Routes & Vehicles
        |
        v
PriorityMTFOptimizerService
        |
        +-> variables.py (x(v,r) binary decision variables)
        +-> objective.py (route cost & congestion overlap weighting)
        +-> qubo.py (H_one_route + H_route_cost + H_congestion)
        +-> solver.py (neal / sa / exact / qpu / dwave with fallback tracking)
        +-> decoder.py (solution decoding & feasibility verification)
        +-> priority_mtf.py (subproblem decomposition & congestion feedback)
        |
        v
OptimizationResult (with SolverMetadata & OptimizationPlan)
```

## Legacy to Migrated Component Mapping

| Legacy Component | Migrated Module | Description |
|---|---|---|
| `priority_aware_mtf.py` | `backend/app/optimization/priority_mtf.py` | MTF subproblem decomposition, iterative solving, and congestion feedback. |
| `priority_aware_mtf.py:build_cost_hamiltonian` | `backend/app/optimization/qubo.py` | Priority-Aware Cost Hamiltonian QUBO construction. |
| `priority_aware_mtf.py:solve_subproblem` | `backend/app/optimization/solver.py` | Multi-solver execution abstraction with transparent fallback metadata. |
| `priority_aware_mtf.py:decode_subproblem` | `backend/app/optimization/decoder.py` | Decodes binary sample into route selections and checks constraint violations. |
| N/A | `backend/app/optimization/service.py` | Public `PriorityMTFOptimizerService` domain wrapper consuming `Network` and `Vehicle` contracts. |

## Decision Variable Mapping

The optimization uses binary decision variables representing candidate route selection:

$$x_{v, r} \in \{0, 1\}$$

where $x_{v, r} = 1$ means vehicle $v$ is assigned candidate route $r$. Variable names are formatted deterministically as `x_{vehicle_id}_{route_idx}`.

## Cost Hamiltonian (QUBO)

$$H_{\text{cost}} = \alpha H_{\text{route\_cost}} + \beta H_{\text{congestion}} + \gamma H_{\text{one\_route}}$$

1. **One-Route Constraint ($H_{\text{one\_route}}$)**:
   Penalizes selecting 0 or $>1$ routes for vehicle $v$: $\gamma (\sum_r x_{v,r} - 1)^2$.
2. **Route Travel Cost ($H_{\text{route\_cost}}$)**:
   Weighted normalized travel cost. For emergency vehicles (ESVs), the weight is amplified: $\alpha \times \text{priority\_weight} \times \text{cost}_{\text{norm}}$.
3. **Congestion Overlap ($H_{\text{congestion}}$)**:
   Penalizes vehicles sharing edge segments:
   - Regular-Regular: $\beta \times 1.0$
   - Emergency-Emergency: $\beta \times 2.0$
   - Emergency-Regular: $\beta \times \text{emergency\_boost}$ (default $10.0$, creating the **green corridor effect**).

## Subproblem Decomposition & Congestion Feedback

1. Vehicles are decomposed into subproblems of size `max_subproblem_size` (default 8).
2. Emergency vehicles are placed in the **first subproblem** to guarantee immediate priority.
3. After solving each subproblem, edge congestion counts increase: $\text{congestion} \leftarrow \text{congestion} + 1$.
4. Edge costs update dynamically: $\text{cost} = \text{base\_time} \times (1.0 + \text{congestion} / 20.0)$.
5. Refined iteratively for `num_iterations` (default 3).

## Solver Identity and Fallback Transparency

When external cloud solvers (D-Wave QPU/Leap) or binary C-extensions (`neal`/`tabu`) fail or encounter environment policy blocks, the solver abstraction transparently falls back to local `dimod.SimulatedAnnealingSampler()` or `ExactSolver()`.

The result explicitly communicates execution class and fallback state:
* `execution_class = CLASSICAL_FALLBACK`
* `fallback_used = True`
* `fallback_reason = "..."`

No classical fallback is ever presented as a quantum hardware execution.

## Limitations

* Stage 7 optimizes **route choice allocation**, not signal phase timing.
* Subproblem decomposition is heuristic and optimizes sub-groups sequentially.
* Edge congestion feedback uses a linear scaling factor ($1.0 + c / 20.0$).
