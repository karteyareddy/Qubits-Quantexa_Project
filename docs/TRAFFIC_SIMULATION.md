# Traffic Simulation

## Scope

Stage 4 provides a deterministic, lightweight discrete-time traffic simulator for the six-intersection demo network. It is a transparent hackathon model, not a calibrated microscopic traffic model and not a substitute for SUMO or field validation.

## Architecture

```text
SimulationScenario
  -> scheduled routed vehicles
  -> TrafficSimulation.reset/step/run
  -> capacity and intersection-entry checks
  -> safely replaceable SimulationState snapshots
```

The simulator consumes the Stage 3 `Network` and `Route` contracts. It does not maintain a second graph representation.

## Timestep and movement

- The default timestep is one simulated second and may be configured per scenario.
- A vehicle moves at the current edge's free-flow speed.
- Distance advanced is `speed_mps * elapsed_seconds`.
- Remaining movement time may carry across multiple route edges in one step.
- A vehicle leaves the network after reaching the target of its final route edge.
- Vehicle processing uses stable vehicle-ID ordering.

This stage does not model acceleration, car-following distance, lane changes, collisions, or stochastic speed variation.

## Capacity and queues

Edge capacity is the maximum number of vehicles occupying an edge. Fractional domain capacity is conservatively converted to an integer with `floor`, with a minimum runtime capacity of one.

A vehicle that cannot enter its next edge remains at its current intersection approach. It stays on its current edge when transitioning between edges, or at its origin before entering the first edge. Queue indexes are derived from waiting vehicle state on every snapshot; they are not synthetic metrics.

Waiting and stopped time increase only for the portion of a timestep during which entry is blocked. Moving vehicles do not accumulate waiting time.

## Intersection policy

`IntersectionEntryPolicy.can_enter_next_edge` is the extension point for Stage 5 signal control. Stage 4 uses `PermitAllIntersections`; the engine still enforces edge closure and capacity independently. No signal phases or signal timing are implemented here.

## Arrivals and scenarios

- Explicit scheduled arrivals support exact vehicle IDs, times, origins, destinations, and emergency metadata.
- Seeded generation uses a local `random.Random` instance and never changes global random state.
- Low-traffic, congested, and emergency-vehicle scenarios use the offline Stage 3 demo network.
- Emergency vehicles retain subtype and priority weight but receive no signal priority in Stage 4.

## State and raw observations

Each JSON-compatible snapshot includes simulation time, pending/active/completed vehicles, waiting vehicles, edge occupancy, edge-entry queues, intersection approach queues, and aggregate pending/active/completed/waiting/throughput counts. Completed vehicles retain travel and waiting times for the later metrics layer.

## Reproducibility

The same network, scenario, seed, timestep, and entry policy produce the same trajectory. IDs are explicit, iteration is sorted, and neither wall-clock timestamps nor global randomness are used.

## Known limitations

- Capacity is a vehicle count rather than a density or lane-flow model.
- Vehicles on the same edge do not interact except through entry capacity.
- The model uses free-flow edge speed and has no acceleration profile.
- Route choice is fixed before simulation; dynamic rerouting belongs to a later stage.
- Traffic signals, events, adaptive control, formal metrics, environmental estimates, optimization, and API publication are intentionally absent.
