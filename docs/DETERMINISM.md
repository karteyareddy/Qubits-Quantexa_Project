# Determinism & Reproducibility Specification

## Overview

This document specifies the seed propagation strategy, deterministic simulation guarantees, and benchmark reproducibility procedures for the Quantum-Enhanced Adaptive Urban Traffic Optimization platform.

## Seed Strategy & Propagation

All pseudo-random state generation within the simulation, routing, scenario creation, and quantum circuit sampling is governed by explicit seed parameters:

1. `seed_all(seed: int)` initializes Python's standard `random` module and `numpy.random`.
2. `SimulationScenario` generators (`low_traffic_scenario`, `congested_traffic_scenario`, `emergency_vehicle_scenario`) accept explicit `seed` parameters to generate vehicle arrival times and route choices deterministically.
3. Quantum QAOA Aer simulators inherit seed configuration for statevector / shot sampling.

## Deterministic Components

The following subsystems are strictly deterministic given an identical seed:

- **Vehicle Spawning & Route Assignment**: Vehicle IDs, routes, and arrival order.
- **Traffic Kinematics & Signal Transitions**: Vehicle position updates, speed adjustments, and fixed-time signal phase transitions.
- **Dynamic Event Execution**: Event scheduler processes due events strictly in order of start time and event ID.
- **QUBO Construction & Variable Ordering**: QUBO matrix generation for signal control produces bitstring variables in canonical lexicographical order.
- **Trajectory Fingerprinting**: `compute_state_trajectory_hash(observations)` generates SHA-256 fingerprints of time, vehicle positions, edge occupancy, and arrival counts.

## Intentionally Nondeterministic Components

- **Wall-clock Optimization Timings**: Real-time performance measurements (`optimization_time_seconds`) depend on host machine CPU/GPU execution speed and operating system thread scheduling.
- **Unseeded Quantum Execution**: If `seed` is omitted or set to `None`, Qiskit Aer uses OS entropy.

## Benchmark Reproducibility Procedure

To reproduce controlled benchmark comparisons (QAOA vs. Classical baseline):

```bash
# Execute Stage 16 benchmark test with fixed seed
python -m pytest backend/tests/unit/test_benchmark.py -v
```

Two runs initialized with identical scenario configurations and seeds produce identical traffic metrics (average travel time, waiting time, completion rate, CO2 emissions) and identical trajectory hashes.
