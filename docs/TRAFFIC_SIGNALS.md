# Traffic Signals

## Scope

Stage 5 provides the deterministic classical fixed-time signal baseline that later quantum and hybrid controllers will be compared against. It does not optimize timings or respond to queues, emergencies, or events.

## Architecture

```text
Stage 3 Network
  -> network-derived incoming SignalApproach records
  -> FixedTimeSignalController per intersection
  -> SignalSystem
  -> FixedTimeSignalPolicy
  -> Stage 4 IntersectionEntryPolicy
```

The simulator asks only whether a vehicle may enter its next edge. It does not know phase schedules or signal implementation details.

## Approach representation

Each approach identifies an intersection, incoming directed edge, source node, and movement axis. Approaches are derived from incoming Stage 3 edges. The axis is calculated from node coordinates as east/west or north/south. Networks without coordinates use deterministic alternating assignment by sorted incoming-edge order; calibrated deployments should always supply coordinates.

The model is road-approach based. It does not represent lanes, turn pockets, protected turns, or pedestrian movements.

## Phase model

The fixed cycle is:

1. east/west green, north/south red;
2. east/west yellow, north/south red;
3. optional all-red clearance;
4. north/south green, east/west red;
5. north/south yellow, east/west red;
6. optional all-red clearance.

Only `GREEN` permits entry. `YELLOW` is treated conservatively as stop for vehicles waiting to enter an intersection. The opposite axis is always `RED`, so conflicting axes are never permitted simultaneously.

## Timing model

Timing uses deterministic integer seconds. Defaults are 20 seconds green, 3 seconds yellow, and 1 second all-red after each axis. The default cycle is 48 seconds. A controller may use a fixed non-negative cycle offset; it never adapts duration during a run.

Signal state depends only on timing configuration, offset, and simulation time. Equivalent cycle positions produce equivalent phases and approach indications.

## Signal snapshots

Serializable snapshots expose intersection ID, current phase, phase start, elapsed and remaining time, cycle position and duration, and every approach's `RED`, `YELLOW`, or `GREEN` indication.

## Simulator integration

At an edge transition, the simulator determines the incoming edge and next-edge intersection, evaluates the signal at the exact crossing time within the timestep, then checks downstream capacity. A vehicle waits on its current approach if either check fails. Signal delay and capacity delay use the same waiting-state mechanism and are never double-counted.

Entering the first route edge does not cross an intersection and is therefore not signal-controlled. Edge closure and capacity remain authoritative regardless of signal state.

## Safety assumptions

- At most one approach axis is green at a time.
- Yellow does not authorize a queued vehicle to enter.
- Optional all-red intervals authorize no approach.
- Unknown incoming approaches at a controlled intersection fail closed.
- Nodes not marked as controlled intersections remain passable through the policy boundary.

## Limitations

- No turning-movement conflict matrix or protected turn phases.
- No detector, queue-responsive, adaptive, emergency-priority, coordinated-offset, or optimization behavior.
- No signal failure modes, pedestrian phases, or field-controller protocol.
- Coordinate-free axis assignment is deterministic but not suitable for calibrated road networks.
- Signal snapshots are internal typed models; API and frontend publication belong to later stages.

Future controllers can replace `FixedTimeSignalPolicy` through the existing simulation `IntersectionEntryPolicy` without rewriting vehicle movement.
