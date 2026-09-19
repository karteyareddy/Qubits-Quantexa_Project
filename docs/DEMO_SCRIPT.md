# Hackathon Presentation & Demo Script

## Overview
This document provides timed presentation scripts (3-minute elevator pitch and 5-minute technical deep dive) for hackathon judging of the Quantum-Enhanced Adaptive Urban Traffic Optimization platform.

---

## 3-Minute Presentation Script (Elevator Pitch)

### 0:00 – 0:30 | Problem & Core Architecture
> "Urban traffic congestion causes billions of hours in lost productivity and excessive CO₂ emissions. Traditional fixed-time signals fail during dynamic events. We built the **Quantum-Enhanced Adaptive Urban Traffic Optimization** platform. It combines discrete-time traffic simulation, Signal-Control QUBO formulations, Qiskit Aer QAOA quantum circuit optimization, and real-time Emergency Green Corridor preemption."

### 0:30 – 1:15 | Live Simulation & Hybrid QAOA
> "On our Next.js dashboard, you can see a 6-intersection network running in real-time. Every 5 seconds, our Python backend observes queue lengths, edge densities, and waiting times. It formulates a Signal-Control QUBO matrix with hard constraints — ensuring exactly one green phase per intersection interval. We solve this QUBO using Quantum Approximate Optimization Algorithm (QAOA) circuits simulated via Qiskit Aer, extracting feasible signal schedules."

### 1:15 – 2:00 | Dynamic Events & Emergency Green Corridor
> "When a dynamic event occurs — like a congestion spike on edge `I1->I2` — the hybrid optimizer re-optimizes signal timing dynamically. Watch what happens when an ambulance registers an emergency mission from `I1` to `I6`: the Emergency Corridor Service plans the optimal route, predicts intersection ETAs, and preempts signals to grant continuous green windows. Notice how non-conflicting traffic is preserved and priority is released cleanly once the ambulance clears."

### 2:00 – 3:00 | Truthful Benchmarks & Conclusion
> "We measure real traffic and environmental metrics — waiting times, throughput, fuel consumption, and CO₂ output — comparing our Hybrid QAOA approach against a Classical Fixed-Time baseline. All benchmark results are truthful: when quantum simulation exceeds qubit limits, fallback to classical heuristics is explicitly reported rather than claiming fake quantum advantage. Thank you!"

---

## 5-Minute Technical Presentation Script (Deep Dive)

### 0:00 – 1:00 | System Architecture
- Introduce Next.js 16 Control Center dashboard, FastAPI REST/WebSocket API, Python domain simulation, and Qiskit Aer integration.
- Highlight clean separation: presentation in Next.js, physics/quantum in Python backend.

### 1:00 – 2:15 | Mathematical Formulation: Signal-Control QUBO & QAOA
- Explain the binary decision variable $x_{i,p,t} \in \{0, 1\}$ representing intersection $i$, phase $p$, interval $t$.
- Detail the QUBO objective components: queue penalties, waiting time reduction, emergency priority weights, phase switching costs, and quadratic penalty terms enforcing exactly one active phase per interval.
- Demonstrate QAOA circuit construction ($p$-layers, ansatz parameter optimization, measurement decoding).

### 2:15 – 3:30 | Dynamic Events & Emergency Preemption
- Demonstrate live injection of `Congestion Spike`, `Accident`, and `Road Closure` events.
- Show emergency preemption lifecycle: `PLANNED` $\rightarrow$ `ACTIVE` $\rightarrow$ `RELEASED`.

### 3:30 – 5:00 | Controlled Benchmarking & Scientific Honesty
- Review matched scenario comparisons under identical initial seeds and demand.
- Highlight scientific honesty: Aer simulation vs. real QPU execution, QUBO energy vs. real-world traffic waiting time, and explicit fallback logging.
