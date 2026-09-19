# Traffic Metrics and Environmental Estimates

## Scope

Stage 6 measures deterministic simulation outcomes. It is independent from routing, signal control, and optimization decisions so the same calculations can evaluate fixed-time and future adaptive or hybrid controllers.

```text
Simulation trajectory and final state
        -> MetricsService
        -> traffic + queue + emergency outcomes
        -> prototype fuel and CO2 estimates
        -> ScenarioMetrics
```

## Vehicle counts and completion

- `total_vehicles`: vehicles that have spawned by the final state. Future pending arrivals are excluded.
- `completed_vehicles`: spawned vehicles that reached their destinations.
- `active_vehicles`: spawned vehicles not completed at the final state.
- `completion_rate`: completed divided by total spawned vehicles, or `0.0` when no vehicles spawned.
- `throughput`: completed vehicles.
- `throughput_per_minute`: completed vehicles divided by elapsed simulation minutes, or `0.0` at zero duration.

The result validates `total_vehicles = completed_vehicles + active_vehicles` and `throughput = completed_vehicles`.

## Waiting metrics

`total_waiting_seconds`, `average_waiting_seconds`, and `max_waiting_seconds` use all spawned vehicles, including incomplete vehicles. The average denominator is `total_vehicles`. This retains delay currently experienced by active traffic instead of hiding it until completion.

Waiting time comes directly from the simulator and covers time blocked by signals or downstream capacity. It is not reconstructed from queue snapshots.

## Travel metrics

`average_travel_seconds` and `max_travel_seconds` use completed vehicles only. Per completed vehicle:

```text
travel time = completion_time_seconds - arrival_time_seconds
```

Incomplete vehicles have `travel_time_seconds = null` in per-vehicle results and never contribute fabricated trip times. Empty completed sets produce `0.0` averages and maxima.

## Queue metrics

- `final_queue_length`: waiting vehicles in the final snapshot.
- `max_queue_length`: largest waiting-vehicle count across supplied observations.
- `average_queue_length`: arithmetic mean waiting-vehicle count across supplied observations.

The caller supplies deterministic simulation snapshots, normally one per simulation step. The final state is included once. If only a final state is supplied, maximum and average describe that single observation; they are not presented as full-run history.

Final edge metrics expose occupancy, edge-entry queue length, and waiting vehicle IDs. Final intersection-approach metrics expose approach queue length and waiting IDs. They remain lightweight final-state observations.

## Per-vehicle results

Results are sorted by vehicle ID and contain vehicle ID, completion status, completed travel time or null, accumulated waiting time, and emergency identity.

## Emergency metrics

Emergency totals include spawned emergency vehicles only. Results expose total, completed, active, completion rate, total waiting, average waiting across all spawned emergency vehicles, and average travel across completed emergency vehicles. Empty emergency sets produce zeros.

These metrics measure emergency outcomes. They do not implement or imply emergency priority.

## Fuel estimate

The configurable prototype model is:

```text
moving_time = max(total_travel_time - waiting_time, 0)
moving_fuel = moving_time_hours * moving_fuel_l_per_hour
idle_fuel = waiting_time_hours * idle_fuel_l_per_hour
fuel_liters = moving_fuel + idle_fuel
```

Default assumptions:

- moving fuel rate: `2.4 L/hour`
- idle fuel rate: `0.08 L/hour`
- CO2 factor: `2.31 kg/liter`

Moving and waiting time do not overlap in the estimate. Per-vehicle values divide scenario totals by spawned vehicles and return zero for an empty scenario.

## CO2 estimate

```text
co2_kg = fuel_liters * co2_kg_per_liter
```

The result explicitly carries `is_estimate = true`.

> Fuel and CO2 values are prototype estimates derived from configurable assumptions; they are not calibrated measurements of actual vehicle emissions.

## Determinism

Calculations contain no randomness or wall-clock input. Vehicle, edge, and approach outputs use stable identifier ordering. The same final state, observations, and environmental configuration produce identical results.

## Limitations

- Environmental rates do not vary by vehicle class, speed, acceleration, grade, temperature, or engine technology.
- Queue averages depend on the observation cadence supplied by the caller.
- Edge and approach breakdowns represent the final state rather than full time-series distributions.
- No fuel or emissions calibration, uncertainty interval, benchmarking, optimization scoring, persistence, API, or frontend is included.
