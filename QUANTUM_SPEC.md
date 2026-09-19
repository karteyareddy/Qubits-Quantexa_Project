# Quantum Specification

## Important distinction

The existing GitHub project primarily formulates route-selection QUBOs using Priority-Aware MTF. The final application must retain that foundation but add a separate signal-control optimization model.

Do not falsely claim that the existing route QUBO alone is an adaptive signal optimizer.

## Signal decision variables

For each intersection and decision horizon:

`x(i,p,d) ∈ {0,1}`

where:
- i = intersection
- p = candidate phase/action
- d = duration option

One legal choice per decision group.

## Objective

Minimize:

`Ww*waiting + Wq*queue + Wc*congestion + We*emergency_time + Wf*fuel + Wco2*co2 + Wt*transition + Wp*constraint_penalty`

Normalize terms before weighting.

Default weights:
- waiting 1.0
- queue 0.8
- congestion 0.8
- emergency 3.0 when active
- fuel 0.3
- CO2 0.3
- transition 1.0
- constraint 10.0

These are tunable defaults, not claims of optimal weights.

## Existing priority-aware routing

Preserve the existing concepts:
- route cost
- congestion cost
- one-route constraint
- emergency priority weighting
- iterative decomposition
- congestion feedback

Use these to provide route candidates and emergency corridor context.

## QAOA

Default:
- Qiskit Aer simulator
- configurable reps
- configurable shots
- classical parameter optimizer

Flow:
QUBO -> Ising-compatible operator -> QAOA -> samples -> decode -> validate -> classical score.

## Fallback

If QAOA errors:
- run explicit classical QUBO fallback
- result solver field = `classical_fallback`
- UI must visibly show fallback.

## Validation

Reject:
- no selected action
- multiple selections
- illegal green duration
- unsafe phase transition
- closed-road emergency route
- corridor conflict
