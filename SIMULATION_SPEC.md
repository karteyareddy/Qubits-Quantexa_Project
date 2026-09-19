# Simulation Specification

## Demo network

```text
I1 ---- I2 ---- I3
|       |       |
I4 ---- I5 ---- I6
```

Bidirectional links by default.

## Tick

Default 5 simulated seconds.

## Vehicle model

At each tick:
1. Determine allowed movement from current signal.
2. Determine capacity.
3. Move vehicles.
4. Update waiting/stopped time.
5. Enter next edge when possible.
6. Record arrivals.
7. Update queues.
8. Reroute if closure invalidates route.

## Signals

Minimum:
- NS_GREEN
- EW_GREEN
- YELLOW
- ALL_RED

Every transition must obey safety timings.

## Events

Congestion:
- increase demand and/or reduce effective capacity.

Accident:
- reduce speed/capacity.

Road closure:
- mark edge unavailable.
- reroute affected traffic.

Emergency:
- create priority vehicle.
- invoke corridor service.

## Metrics

Per tick:
- active vehicles
- arrived vehicles
- average waiting
- total waiting
- queue length
- throughput
- emergency travel time
- fuel estimate
- CO2 estimate

## Environmental estimate

Use configurable coefficients:
`fuel = idle_rate * stopped_time + distance_rate * distance`

`co2 = fuel * co2_factor`

Always label as estimates.
