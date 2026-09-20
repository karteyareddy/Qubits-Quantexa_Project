<p align="center">
  <img src="frontend/public/q-trafficx-logo.png" alt="Q-TrafficX Logo" width="300" />
</p>

<h1 align="center">Q-TrafficX</h1>
<h3 align="center">Quantum-Enhanced Adaptive Urban Traffic Optimization & Emergency Routing</h3>
<p align="center">
  <em>Smarter Roads • Safer Cities • Greener Tomorrow</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Next.js-14+-black?style=for-the-badge&logo=next.js&logoColor=white" alt="Next.js" />
  <img src="https://img.shields.io/badge/React-18%2F19-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React" />
  <img src="https://img.shields.io/badge/Qiskit-1.0+-6929C4?style=for-the-badge&logo=qiskit&logoColor=white" alt="Qiskit" />
  <img src="https://img.shields.io/badge/Qiskit%20Aer-Simulation-blueviolet?style=for-the-badge" alt="Qiskit Aer" />
  <img src="https://img.shields.io/badge/Status-Validated-success?style=for-the-badge" alt="Status" />
</p>

---

## 📑 Table of Contents
- [1. What is Q-TrafficX?](#1-what-is-q-trafficx)
- [2. Why Q-TrafficX? (The Problem Statement)](#2-why-q-trafficx-the-problem-statement)
- [3. The Solution & Core Value Proposition](#3-the-solution--core-value-proposition)
- [4. Technical Approach & Mathematical Foundations](#4-technical-approach--mathematical-foundations)
  - [4.1 Global Traffic Cost Objective](#41-global-traffic-cost-objective)
  - [4.2 QUBO Formulation](#42-qubo-formulation)
  - [4.3 Ising Spin Hamiltonian Transformation](#43-ising-spin-hamiltonian-transformation)
  - [4.4 QAOA Circuit Ansatz & Optimization](#44-qaoa-circuit-ansatz--optimization)
  - [4.5 Microscopic Kinematic Traffic Simulation](#45-microscopic-kinematic-traffic-simulation)
  - [4.6 Dynamic Emergency Green Corridors](#46-dynamic-emergency-green-corridors)
  - [4.7 Dynamic Incident & Event Management](#47-dynamic-incident--event-management)
- [5. System Architecture & Tech Stack](#5-system-architecture--tech-stack)
- [6. Requirements & Verification Matrix](#6-requirements--verification-matrix)
- [7. Project Directory Structure](#7-project-directory-structure)
- [8. Installation & Setup Guide](#8-installation--setup-guide)
  - [8.1 Prerequisites](#81-prerequisites)
  - [8.2 Step-by-Step Installation](#82-step-by-step-installation)
  - [8.3 Launching the Application](#83-launching-the-application)
  - [8.4 Environment Configuration](#84-environment-configuration)
- [9. Operator Guide & Interactive Demonstration](#9-operator-guide--interactive-demonstration)
- [10. Testing, Linting & Quality Verification](#10-testing-linting--quality-verification)
- [11. Scientific Honesty & Quantum Modeling Disclosures](#11-scientific-honesty--quantum-modeling-disclosures)
- [12. Acknowledgments](#12-acknowledgments)

---

## 1. What is Q-TrafficX?

**Q-TrafficX** is a next-generation, quantum-enhanced urban traffic orchestration and emergency priority routing platform. It bridges continuous microscopic vehicular simulation with quantum combinatorial optimization to eliminate urban traffic bottlenecks, drastically cut idling emissions, and guarantee non-preempted green waves for emergency response vehicles.

Designed with a modular architecture, **Q-TrafficX** couples a high-performance **FastAPI** backend with a modern **Next.js** operations console, giving municipal traffic authorities, emergency dispatchers, and urban engineers real-time observability and adaptive closed-loop control over interconnected arterial road networks.

---

## 2. Why Q-TrafficX? (The Problem Statement)

Urban road networks worldwide are plagued by outdated, rigid traffic control paradigms:

1. **Exponential Combinatorial Explosion ($O(2^N)$)**:
   Coordinating multi-intersection signal splits and offsets across an interconnected arterial grid is an NP-hard combinatorial problem. As intersection counts and phase permutations grow, classical brute-force algorithms scale exponentially, rendering global real-time synchronization computationally intractable.
2. **Rigid Fixed-Time & Actuated Limits**:
   Conventional traffic lights run on pre-programmed time-of-day tables or isolated loop detectors. They fail during unexpected traffic surges, dynamic accidents, or adverse weather conditions, leading to upstream queue spillbacks and gridlock.
3. **Emergency Service Delays & Fatalities**:
   Ambulances, fire services, and police units lose critical response minutes trapped in general queue queues or caught at red lights. Traditional siren-based optical or radio preemption is localized to a single junction and lacks network-wide route lookahead.
4. **Severe Environmental and Economic Costs**:
   Stop-and-go driving and intersection idling account for millions of tons of excess $\text{CO}_2$ emissions and wasted fuel each year, degrading urban air quality and contributing directly to climate change.

---

## 3. The Solution & Core Value Proposition

**Q-TrafficX** transforms traffic signal control from static schedules into a live, dynamically responsive optimization surface:

* **Quantum-Accelerated Combinatorial Optimization**: Formulates coordinated signal timing into Quadratic Unconstrained Binary Optimization (QUBO) and Ising Hamiltonians, solved via the Quantum Approximate Optimization Algorithm (QAOA) on **Qiskit Aer** quantum circuit simulation.
* **Continuous Microscopic Vehicle Modeling**: Models individual vehicle kinematics, car-following behaviors, queue build-up, and lane saturation capacities across connected arterial junctions.
* **Dynamic Emergency Green Corridors**: Automatically reserves and propagates an uninterrupted green wave along an ambulance’s exact GPS path, ensuring zero signal delay while gracefully managing cross-traffic queue dissipation.
* **Live Dynamic Incident Adaptation**: Automatically recalculates signal allocations when real-world disruptions (accidents, lane closures, weather slowdowns) occur.
* **Real-Time Operational Console**: Delivers live canvas arterial rendering, interactive transport controls, incident injection modal, LED matrix pulse loaders (`LatticeLoader`), and comprehensive environmental telemetry.

---

## 4. Technical Approach & Mathematical Foundations

```mermaid
flowchart LR
    A[Microscopic Traffic State\nQueues • Speeds • Densities] --> B[QUBO & Objective Builder\nArterial Coupling Matrix]
    B --> C[Ising Spin Transformation\nPauli-Z Mapping]
    C --> D[QAOA Quantum Simulator\nQiskit Aer Circuit]
    D --> E[Candidate Bitstrings\n& Energy Sampling]
    E --> F[Classical Refinement\n& Feasibility Filter]
    F --> G[Adaptive Signal Execution\nGreen Splits & Corridors]
```

### 4.1 Global Traffic Cost Objective
The multi-objective cost function minimizes cumulative waiting time, queue backlogs, arterial link density, and signal switching penalties while prioritizing emergency vehicles:

$$\mathcal{C}_{\text{traffic}} = W_w \sum_{i} \text{Wait}_i + W_q \sum_{i} \text{Queue}_i + W_c \sum_{e} \text{Congestion}_e - W_e \cdot \text{EmergencyBonus} + W_t \cdot \text{TransitionPenalty}$$

Where:
* $W_w, W_q$: Weights penalizing observed vehicle delay and stopped queue length.
* $W_c$: Congestion penalty on road links exceeding their saturation threshold $\rho > 0.75$.
* $W_e$: High-priority bonus multiplier awarded to active emergency corridors.
* $W_t$: Damping penalty preventing unnecessary rapid phase thrashing.

---

### 4.2 QUBO Formulation
Signal phase decisions are encoded into binary decision variables $x_{i, p} \in \{0, 1\}$, indicating whether phase $p$ is active at intersection $i$:

$$\min_{x \in \{0, 1\}^N} E(x) = \sum_{i} Q_{ii} x_i + \sum_{i < j} Q_{ij} x_i x_j + c$$

* **Linear Diagonal Terms ($Q_{ii}$)**: Quantify the traffic pressure and queue discharge deficit relieved by activating phase $i$.
* **Quadratic Coupling Terms ($Q_{ij}$)**: Represent network coordination between adjacent intersections $i$ and $j$, heavily discounting concurrent green signals along shared arterial progression corridors (creating green waves).
* **One-Hot Phase Constraint**: Enforces that each intersection operates exactly one legal active phase at any given instant via penalty multiplier $P$:

$$P_{\text{one-hot}} = P \sum_{k} \left( \sum_{p \in \text{Phases}_k} x_{k, p} - 1 \right)^2$$

---

### 4.3 Ising Spin Hamiltonian Transformation
To execute on quantum architectures, binary variables $x_i \in \{0, 1\}$ are mapped to quantum spin operators $z_i \in \{-1, +1\}$ via the exact substitution:

$$x_i = \frac{I - Z_i}{2}$$

Substituting this into the QUBO yields the Ising Problem Hamiltonian $H_C$:

$$H_C = \sum_{i=1}^N h_i Z_i + \sum_{i < j} J_{ij} Z_i Z_j + c_{\text{Ising}} I$$

Where local magnetic field coefficients $h_i$ and 2-qubit spin couplings $J_{ij}$ are calculated analytically:

$$h_i = -\frac{Q_{ii}}{2} - \sum_{j \neq i} \frac{Q_{ij}}{4}, \quad J_{ij} = \frac{Q_{ij}}{4}$$

---

### 4.4 QAOA Circuit Ansatz & Optimization
The Quantum Approximate Optimization Algorithm prepares a parameterized quantum state over $p$ alternating circuit layers:

$$|\psi(\boldsymbol{\gamma}, \boldsymbol{\beta})\rangle = \prod_{l=1}^p \left( e^{-i \beta_l H_M} e^{-i \gamma_l H_C} \right) |+\rangle^{\otimes N}$$

1. **Initial State**: Uniform superposition across all computational basis states $|+\rangle^{\otimes N} = H^{\otimes N} |0\rangle^{\otimes N}$.
2. **Phase Separator $e^{-i \gamma_l H_C}$**: Encodes the problem cost through $R_Z(\theta)$ single-qubit rotations and $R_{ZZ}(\theta)$ two-qubit entangling gates.
3. **Mixer Hamiltonian $H_M = \sum_{i=1}^N X_i$**: Transverse field driving quantum transitions between orthogonal configurations using $R_X(2\beta_l)$ gates.
4. **Classical Parameter Loop**: The expectation value $\langle \psi(\boldsymbol{\gamma}, \boldsymbol{\beta}) | H_C | \psi(\boldsymbol{\gamma}, \boldsymbol{\beta}) \rangle$ is minimized using the classical **COBYLA** optimizer on **Qiskit Aer** (`AerSimulator`), sampling top candidate bitstrings that undergo fast 1-bit flip classical heuristic refinement.

---

### 4.5 Microscopic Kinematic Traffic Simulation
Vehicular movement follows discrete-time microscopic kinematics with car-following safety constraints:
* **Position & Velocity Updates**: $v(t + \Delta t) = \min(v_{\text{target}}, v(t) + a_{\text{max}} \Delta t)$, clamped by distance to preceding vehicle.
* **Lane Capacity & Queuing**: Continuous density monitoring $\rho_e = \frac{N_{\text{active}}}{C_{\text{capacity}}}$ across every arterial link.
* **Environmental Models**: Moving fuel consumption ($2.4 \text{ L/hr}$) and idling fuel burn ($0.08 \text{ L/hr}$) converted to $\text{CO}_2$ emissions ($2.31 \text{ kg } \text{CO}_2\text{/L}$) via standard EPA vehicle emission factors.

---

### 4.6 Dynamic Emergency Green Corridors
When an emergency vehicle is dispatched:
1. **Dynamic Path Calculation**: The optimal network route from origin to hospital/destination is computed.
2. **Preemptive Signal Preemption**: Upcoming intersections along the corridor calculate the vehicle’s Estimated Time of Arrival (ETA) and dynamically extend or switch signals to green prior to arrival.
3. **Safe Dissipation**: Cross-street queues accumulated during corridor activation are smoothly discharged using priority-compensated phase cycles post-passage.

---

### 4.7 Dynamic Incident & Event Management
The simulation includes an event engine capable of introducing realistic urban disruptions on the fly:
* **Road Accidents**: Obstruction of active lanes, reducing throughput to zero or near-zero on affected segments.
* **Lane Closures**: Scheduled or emergency lane restrictions halving link capacity.
* **Weather Slowdowns**: Rainfall or fog reducing maximum vehicle cruising speed by 30–50%.
* **Traffic Surges**: Sudden influx of vehicles testing network absorption resilience.

---

## 5. System Architecture & Tech Stack

```mermaid
flowchart TB
    subgraph Client["Frontend Client (Next.js 14 • Port 3000)"]
        HeroPage["Landing / Hero Page (/)"]
        ConsolePage["Operations Console (/console)"]
        CanvasMap["2D Arterial Canvas Map"]
        Controls["Transport & Speed Multipliers (1x, 2x, 5x)"]
        Telemetry["Environmental & Performance Cards"]
        Lattice["LED Matrix Pulse Loader (LatticeLoader)"]
        EventModal["Incident Injection Modal"]
    end

    subgraph Server["Backend Service (FastAPI • Python 3.11 • Port 8000)"]
        Router["REST API Endpoints (/api/v1)"]
        WSManager["WebSocket Telemetry Streamer (/ws)"]
        
        subgraph CoreSim["Simulation Engine"]
            Network["6-Node Arterial Graph"]
            Kinematics["Microscopic Kinematics"]
            Observer["Traffic State Observer"]
        end

        subgraph Optimizer["Optimization Engine"]
            QUBO["Signal QUBO Generator"]
            Ising["Ising Hamiltonian Converter"]
            QAOA["Qiskit Aer Simulator"]
            Refiner["Classical Bitstring Refiner"]
        end

        subgraph Preemption["Emergency Preemption Core"]
            Tracker["Ambulance GPS & ETA Engine"]
            Corridor["Green Wave Coordinator"]
        end
    end

    ConsolePage <-->|REST API Requests| Router
    ConsolePage <-->|WebSocket Stream (100ms)| WSManager
    Router --> CoreSim
    Router --> Optimizer
    Router --> Preemption
    CoreSim --> WSManager
```

### Core Technology Stack
| Layer | Technologies |
|---|---|
| **Frontend Framework** | Next.js 14, React 18/19, TypeScript (Strict Mode) |
| **Styling & Design** | Vanilla CSS Design System, Custom Glassmorphism, Dark & Light Themes |
| **Visual Rendering** | HTML5 2D Canvas (60 FPS vehicle rendering, headlights, signal heads) |
| **Backend API** | FastAPI, Uvicorn, Pydantic v2 (Strict Schema Validation) |
| **Quantum Simulation** | Qiskit 1.0+, Qiskit Aer (`AerSimulator`) |
| **Graph & Networks** | NetworkX (6-Node Metropolitan Arterial Topology) |
| **Optimization Stack** | dimod (BQM), Neal (Simulated Annealing), SciPy (COBYLA) |

---

## 6. Requirements & Verification Matrix

All 24 core capabilities are fully implemented, tested, and validated:

| # | Requirement | Implementation Module | Verified Status |
|---|---|---|---|
| 1 | **Traffic Optimization** | `backend/app/adaptive/controller.py` | ✅ Fully Implemented |
| 2 | **Quantum Optimization** | `backend/app/quantum/qaoa.py` | ✅ Fully Implemented |
| 3 | **QUBO Formulation** | `backend/app/signals/qubo/builder.py` | ✅ Fully Implemented |
| 4 | **Ising Formulation** | `backend/app/quantum/ising.py` | ✅ Fully Implemented |
| 5 | **QAOA Circuit Execution** | `backend/app/quantum/circuit.py` | ✅ Fully Implemented |
| 6 | **Hybrid Quantum-Classical** | `backend/app/optimization/hybrid_solver.py` | ✅ Fully Implemented |
| 7 | **4–8 Connected Intersections** | `backend/app/simulation/scenarios.py` (6 Nodes) | ✅ Fully Implemented |
| 8 | **Traffic Density** | `backend/app/simulation/road.py` | ✅ Fully Implemented |
| 9 | **Queue Length Tracking** | `backend/app/metrics/performance.py` | ✅ Fully Implemented |
| 10 | **Road Capacity Limits** | `backend/app/domain/network.py` | ✅ Fully Implemented |
| 11 | **Signal Status Lifecycle** | `backend/app/domain/signal.py` | ✅ Fully Implemented |
| 12 | **Adaptive Green-Light Duration**| `backend/app/adaptive/rules.py` | ✅ Fully Implemented |
| 13 | **Emergency Vehicle Modeling** | `backend/app/emergency/vehicle.py` | ✅ Fully Implemented |
| 14 | **Emergency Green Corridor** | `backend/app/emergency/corridor.py` | ✅ Fully Implemented |
| 15 | **Dynamic Events (Accidents)** | `backend/app/events/handlers.py` | ✅ Fully Implemented |
| 16 | **Waiting Time Metric** | `backend/app/metrics/performance.py` | ✅ Fully Implemented |
| 17 | **Traffic Throughput (v/h)** | `backend/app/metrics/performance.py` | ✅ Fully Implemented |
| 18 | **Fuel Consumption Model** | `backend/app/metrics/environmental.py` | ✅ Fully Implemented |
| 19 | **CO₂ Emissions Tracking** | `backend/app/metrics/environmental.py` | ✅ Fully Implemented |
| 20 | **Classical Comparison** | `backend/app/benchmark/runner.py` | ✅ Fully Implemented |
| 21 | **Interactive Dashboard** | `frontend/app/console/page.tsx` | ✅ Fully Implemented |
| 22 | **Road Network Visualization** | `frontend/components/traffic/TrafficMap.tsx` | ✅ Fully Implemented |
| 23 | **Emergency Route Display** | `TrafficMap.tsx` & `EmergencyCorridorPanel` | ✅ Fully Implemented |
| 24 | **Classical vs Quantum Results** | `frontend/components/quantum/ClassicalComparison.tsx` | ✅ Fully Implemented |

---

## 7. Project Directory Structure

```text
Quantum-Traffic-Priority-Routing/
├── backend/
│   ├── app/
│   │   ├── adaptive/         # Adaptive signal control rules & cycle calculators
│   │   ├── api/              # FastAPI REST routers & WebSocket connection manager
│   │   ├── benchmark/        # Classical vs. Quantum comparison runners
│   │   ├── core/             # Validated configuration & application settings
│   │   ├── domain/           # Network graph, road link, intersection, and signal models
│   │   ├── emergency/        # Emergency vehicle dispatch & green wave service
│   │   ├── events/           # Dynamic incident handlers (accidents, closures, weather)
│   │   ├── metrics/          # Delay, throughput, fuel consumption, and CO2 models
│   │   ├── optimization/     # Hybrid quantum-classical decomposition & solvers
│   │   ├── quantum/          # Qiskit Aer QAOA, Ising converter, & ansatz circuits
│   │   ├── signals/qubo/     # QUBO builder, objective matrices, and solution decoders
│   │   └── simulation/       # Microscopic vehicle simulation engine & scenarios
│   └── tests/
│       ├── unit/             # 38 unit test modules covering all subsystems
│       └── integration/      # End-to-end simulation lifecycle & API tests
├── frontend/
│   ├── app/
│   │   ├── layout.tsx        # Root layout with ThemeProvider and brand typography
│   │   ├── page.tsx          # Standalone Landing / Hero Page
│   │   ├── console/page.tsx  # Full Operations Console
│   │   └── globals.css       # Complete Vanilla CSS Design System (Dark & Light)
│   ├── components/
│   │   ├── dashboard/        # Header, ControlPanel, Sidebar
│   │   ├── emergency/        # EmergencyCorridorPanel
│   │   ├── events/           # EventInjectionModal, EventTimeline
│   │   ├── metrics/          # MetricCards, MetricTrends
│   │   ├── quantum/          # QuantumPanel, ClassicalComparison
│   │   ├── traffic/          # TrafficMap (Interactive Canvas), IntersectionModal
│   │   └── ui/               # LatticeLoader (Custom LED matrix pulse animation)
│   └── public/               # Official Q-TrafficX brand logos and icons
├── docs/                     # Comprehensive architecture, API, and QA specifications
├── Makefile                  # Build, test, and execution commands
└── README.md                 # Master project documentation
```

---

## 8. Installation & Setup Guide

### 8.1 Prerequisites
Ensure your workstation meets the following minimum requirements:
* **Operating System**: Windows 10/11, macOS (Apple Silicon or Intel), or Linux (Ubuntu 20.04+)
* **Python**: `3.11` or `3.12`
* **Node.js**: `20.x` LTS or higher
* **npm**: `10.x` or higher
* **Git**: Installed and configured

---

### 8.2 Step-by-Step Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/karteyareddy/Qubits-Quantexa_Project.git
cd Qubits-Quantexa_Project
```

#### 2. Create and Activate Python Virtual Environment
* **On Windows (PowerShell / Command Prompt)**:
  ```powershell
  python -m venv .venv
  .venv\Scripts\activate
  ```
* **On macOS / Linux**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

#### 3. Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

### 8.3 Launching the Application

You will run the backend and frontend in two separate terminals.

#### Terminal 1: Start the Backend Server (FastAPI on Port 8000)
```bash
# Make sure virtual environment is active (.venv)
python -m uvicorn app.api.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```
* The API will initialize and listen at: `http://127.0.0.1:8000`
* Interactive API Documentation (Swagger UI): `http://127.0.0.1:8000/docs`

#### Terminal 2: Start the Frontend Application (Next.js on Port 3000)
```bash
cd frontend
npm run dev
```
* The web application will launch at: `http://localhost:3000`

---

### 8.4 Environment Configuration

Environment settings are backed by validated Pydantic models. Optional local overrides can be configured via `.env`:

```env
# Backend Settings
APP_ENV=development
HOST=127.0.0.1
PORT=8000
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Simulation Core
RANDOM_SEED=42
SIM_TICK_SECONDS=1.0
OPTIMIZATION_INTERVAL_SECONDS=5.0
MAX_SIMULATION_DURATION_SECONDS=3600.0

# Quantum QAOA Simulation
QAOA_REPS=1
QAOA_SHOTS=256
MAX_QAOA_QUBITS=30

# Logging
LOG_LEVEL=INFO

# Frontend Public Variables
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/simulation
```

---

## 9. Operator Guide & Interactive Demonstration

Follow these steps to explore all capabilities of **Q-TrafficX**:

1. **Visit the Landing Page (`/`)**:
   * Open `http://localhost:3000` in your browser.
   * Explore the presentation of the Q-TrafficX mission, core metrics, and architecture.
   * Click **`Launch Traffic Console →`** to navigate to the operations center.

2. **Start Microscopic Traffic Simulation**:
   * On the Operations Console (`/console`), choose a scenario from the dropdown:
     * `Low Traffic (3 vehicles)`: Ideal for inspecting individual vehicular trajectories and signal switches.
     * `Congested Traffic (12 vehicles)`: Demonstrates heavy queue dynamics and arterial backpressure.
   * Click **`▶ Start`** to start continuous simulation.
   * Use the speed multipliers (**`1×`**, **`2×`**, **`5×`**) to accelerate network progression.
   * Use **`⏸ Pause`**, **`⏭ Step 1s`**, or **`⏩ Skip +10s`** for fine-grained inspection.

3. **Inspect the Interactive 2D Road Network**:
   * Observe vehicles moving across the 6-intersection arterial network with illuminated headlights and dynamic braking colors.
   * Watch intersection signals cycle between Green, Yellow, and Red.
   * Click directly on any intersection circle ($I_1$ through $I_6$) to view its live queue depths and active phase splits in the **Intersection Inspector**.

4. **Trigger Quantum QAOA Optimization**:
   * Click **`⚛ Optimize Now`** in the control toolbar.
   * The custom **LatticeLoader** (animated LED matrix pulse) indicates active statevector sampling and parameter tuning.
   * Inspect the **Hybrid Quantum Optimizer** card to view the sampled ground-state energy, execution time (in milliseconds), and optimal phase recommendations.

5. **Inject Dynamic Road Incidents**:
   * Click **`⚡ Inject Event`** to open the Incident Modal.
   * Choose an incident type:
     * **Road Accident**: Halts movement on a designated link.
     * **Lane Closure**: Halves link capacity to simulate construction.
     * **Weather Slowdown**: Reduces cruising speeds across the arterial corridor.
     * **Traffic Surge**: Spawns sudden vehicle clusters to stress-test adaptive control.
   * Observe how the network responds and adjusts signal splits.

6. **Activate Emergency Green Wave Corridor**:
   * Locate the **Emergency Corridor** card on the dashboard.
   * Select an origin ($I_1$) and destination ($I_6$) and click **`Activate Corridor`**.
   * A priority emergency vehicle (ambulance) is dispatched with high siren priority ($w_e \gg 1$).
   * Watch the corridor route glow on the map as upcoming signals are preemptively turned and held green until the vehicle safely passes.

7. **Analyze Real-Time Telemetry & Environmental Metrics**:
   * Review live metrics updating in real time:
     * **Average Wait Time** per vehicle (seconds).
     * **Network Throughput** (vehicles/hour).
     * **Fuel Burn Model** (liters consumed).
     * **$\text{CO}_2$ Footprint** (kilograms emitted).
   * Review the **Classical vs. Hybrid Optimization** comparison table to evaluate QAOA performance against fixed-time control.

8. **Theme Customization**:
   * Toggle between **Dark Mode** (Cyber Obsidian) and **Light Mode** (Crisp Professional) via the top navigation toggle.

---

## 10. Testing, Linting & Quality Verification

Q-TrafficX enforces strict quality gates with comprehensive test coverage:

```bash
# Run backend unit and integration test suite
python -m pytest backend/tests -v

# Run unit tests only
python -m pytest backend/tests/unit -v

# Run integration tests only
python -m pytest backend/tests/integration -v

# Run Python code formatting & linting (Ruff)
ruff check backend

# Run Python static type analysis (Mypy)
mypy backend/app

# Run Frontend production build (Next.js)
cd frontend
npm run build
```

---

## 11. Scientific Honesty & Quantum Modeling Disclosures

In adherence to strict scientific and engineering rigor:
* **Quantum Simulation**: All QAOA executions in this platform run on the **Qiskit Aer** quantum circuit simulator (`AerSimulator`). They model true quantum state preparation, parameterized unitary rotations, and projective measurement sampling, but run locally on classical host hardware without asserting physical quantum advantage.
* **Deterministic Fallback**: When problem dimensions exceed simulated qubit limits ($> 30$ variables), the system automatically routes execution through classical simulated annealing or greedy heuristic baselines, recording transparent metadata with the execution class explicitly tagged as `CLASSICAL_FALLBACK`.
* **Environmental Estimation**: Fuel consumption and greenhouse gas figures are calculated via standard domain kinematic approximations (moving vs. idling consumption rates) and serve as relative comparative indicators.

---

## 12. Acknowledgments

* **Quantum Computing Framework**: [Qiskit](https://qiskit.org/) by IBM Quantum & [Qiskit Aer](https://github.com/Qiskit/qiskit-aer).
* **Backend Infrastructure**: [FastAPI](https://fastapi.tiangolo.com/) & [Pydantic](https://docs.pydantic.dev/).
* **Frontend Experience**: [Next.js](https://nextjs.org/) & [React](https://react.dev/).
* **Branding & Architecture**: **Q-TrafficX** — *Smarter Roads • Safer Cities • Greener Tomorrow*.
