<p align="center">
  <img src="frontend/public/q-trafficx-logo.png" alt="Q-TrafficX Logo" width="280" />
</p>

<h1 align="center">Q-TrafficX</h1>
<h3 align="center">Quantum Adaptive Traffic Optimization</h3>
<p align="center">
  <em>Smarter Roads • Safer Cities • Greener Tomorrow</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Next.js-16.3-black?style=for-the-badge&logo=next.js&logoColor=white" alt="Next.js" />
  <img src="https://img.shields.io/badge/React-19.3-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Qiskit-1.0+-6929C4?style=for-the-badge&logo=qiskit&logoColor=white" alt="Qiskit" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License" />
</p>

---

## 📖 Executive Overview

**Q-TrafficX** is an end-to-end, production-grade urban traffic optimization platform that combines:
1. **Deterministic Microscopic Traffic Simulation**: Continuous modeling of vehicle kinematics, lane capacities, queue accumulation, and signal states.
2. **Signal-Control QUBO & Ising Formulation**: Formulating multi-intersection signal control into quadratic binary optimization and Ising spin Hamiltonians.
3. **Quantum Approximate Optimization Algorithm (QAOA)**: Executing parameterized quantum circuits on Qiskit Aer (`AerSimulator`) to discover minimum-energy signal phase combinations.
4. **Hybrid Quantum-Classical Architecture**: Classical problem decomposition paired with quantum ansatz state evaluation and heuristic verification.
5. **Emergency Green Corridors**: Dynamic priority routing that preemptively synchronizes green waves for ambulances and emergency responders.
6. **Real-Time Interactive Next.js 16 Console**: Featuring live 2D canvas arterial maps, custom LED matrix pulse loaders (`LatticeLoader`), telemetry trends, incident injection, and seamless Dark/Light theme switching.

---

## 📐 System Architecture

```mermaid
flowchart TB
    subgraph Frontend["Frontend Client (Next.js 16 • Port 3000)"]
        Hero["Standalone Hero Page (/)"]
        Console["Operations Console (/console)"]
        Map["2D Interactive Traffic Map Canvas"]
        Controls["Transport & Speed Controls (1x, 2x, 5x)"]
        MetricsView["Environmental & Telemetry Cards"]
        QuantumView["Hybrid QAOA Status & Benchmark Panel"]
        EmergencyView["Emergency Green Wave Corridor Panel"]
    end

    subgraph Backend["Backend Engine (FastAPI • Python 3.11 • Port 8000)"]
        REST["REST API Endpoints (/api/v1)"]
        WS["WebSocket State Streamer (/ws)"]
        
        subgraph SimEngine["Simulation Core"]
            Network["6-Node Connected Arterial Network"]
            MicroSim["Microscopic Kinematic Simulator"]
            AdaptiveCtl["Adaptive Signal Controller"]
            MetricsCalc["Performance & Environmental Models"]
        end
        
        subgraph Events["Dynamic Event Engine"]
            Accidents["Accidents & Obstructions"]
            Closures["Lane Closures & Capacity Drops"]
            Surges["Congestion & Flow Spikes"]
        end

        subgraph Emergency["Emergency Preemption Core"]
            VehicleTracker["Ambulance GPS & ETA Estimator"]
            CorridorCoord["Green Wave Signal Overrider"]
        end

        subgraph Quantum["Quantum Optimization Pipeline"]
            QUBO["QUBO Objective & Penalty Builder"]
            Ising["QUBO-to-Ising Spin Converter"]
            QAOA["Qiskit Aer QAOA Circuit Solver"]
            Classical["Classical Benchmark & Fallback Solvers"]
        end
    end

    Console <-->|REST HTTP| REST
    Console <-->|Live Telemetry (100ms)| WS
    REST --> SimEngine
    REST --> Events
    REST --> Emergency
    REST --> Quantum
    SimEngine --> MetricsCalc
    Emergency --> AdaptiveCtl
    Quantum --> AdaptiveCtl
```

---

## 🎯 Requirements & Compliance Checklist

All 24 core capabilities are fully implemented, tested, and validated:

| Capability | Module / Component | Implementation Details |
|---|---|---|
| **Traffic Optimization** | `backend/app/adaptive/controller.py` | Dynamically optimizes green splits, offsets, and cycle lengths. |
| **Quantum Optimization** | `backend/app/quantum/qaoa.py` | Parameterized quantum circuits executed on Qiskit Aer (`AerSimulator`). |
| **QUBO Formulation** | `backend/app/signals/qubo/builder.py` | Quadratic cost matrix with queue weights and arterial coupling. |
| **Ising Formulation** | `backend/app/quantum/ising.py` | Exact transformation: $x_i = \frac{1 - z_i}{2} \implies H = \sum h_i Z_i + \sum J_{ij} Z_i Z_j$. |
| **QAOA** | `backend/app/quantum/circuit.py` | Multi-layer parameterized ansatz $U(C, \gamma) U(B, \beta)$ with COBYLA. |
| **Hybrid Quantum-Classical** | `backend/app/optimization/hybrid_solver.py` | Classical decomposition + quantum statevector sampling + heuristic verification. |
| **4–8 Connected Intersections** | `backend/app/simulation/scenarios.py` | **6-node metropolitan network** ($I_1$ to $I_6$) with bidirectional arterials. |
| **Traffic Density** | `backend/app/simulation/road.py` | Real-time link density $\rho = \frac{N_{\text{veh}}}{C_{\text{road}}}$ with congestion heat coloring. |
| **Queue Length** | `backend/app/metrics/performance.py` | Tracks stopped queue lengths per intersection approach lane. |
| **Road Capacity** | `backend/app/domain/network.py` | Distinct lane saturation limits (15–30 vehicles per arterial segment). |
| **Signal Status** | `backend/app/domain/signal.py` | Real-time phase states (`NS_GREEN`, `EW_GREEN`, `YELLOW`, `ALL_RED`). |
| **Adaptive Green-Light** | `backend/app/adaptive/rules.py` | Dynamic green extensions (15s to 60s) based on observed pressure. |
| **Emergency Vehicle** | `backend/app/emergency/vehicle.py` | Priority ambulances with siren weight multipliers ($w_{\text{priority}} \gg 1$). |
| **Emergency Green Corridor** | `backend/app/emergency/corridor.py` | Preemptively synchronizes signals along ambulance routes ahead of arrival. |
| **Dynamic Events** | `backend/app/events/handlers.py` | Injects accidents, lane closures, weather slowdowns, and traffic surges. |
| **Waiting Time** | `backend/app/metrics/performance.py` | Average and cumulative signal delay per vehicle in seconds. |
| **Traffic Throughput** | `backend/app/metrics/performance.py` | Vehicles successfully clearing network per hour (`v/h`). |
| **Fuel Consumption** | `backend/app/metrics/environmental.py` | Moving vs. idling burn model ($2.4\text{ L/hr moving} + 0.08\text{ L/hr idle}$). |
| **CO₂ Emissions** | `backend/app/metrics/environmental.py` | Direct emission calculations based on fuel burn ($2.31\text{ kg CO}_2\text{/L}$). |
| **Classical Comparison** | `backend/app/benchmark/runner.py` | Compares QAOA against Classical Fixed-Time control and Exact QUBO. |
| **Interactive Dashboard** | `frontend/app/console/page.tsx` | Play, Pause, Step 1s, Skip +10s, Stop, Speed multipliers (1×, 2×, 5×). |
| **Road Network Visualization** | `frontend/components/traffic/TrafficMap.tsx` | Interactive 2D map with vehicle headlights, street names, and signal heads. |
| **Emergency Route Display** | `TrafficMap.tsx` & `EmergencyPanel` | Luminous emergency corridor overlay with live vehicle tracking. |
| **Classical vs Quantum Results** | `frontend/components/quantum/` | Compares objective energy, computation runtime (ms), and feasibility. |

---

## 🔬 Mathematical & Quantum Formulations

### 1. The Traffic Cost Objective
The global signal objective balances queue pressure, vehicle delay, arterial congestion, emergency transit, and transition overhead:

$$\mathcal{C}_{\text{traffic}} = W_w \sum_{i} \text{Wait}_i + W_q \sum_{i} \text{Queue}_i + W_c \sum_{e} \text{Congestion}_e - W_e \cdot \text{EmergencyBonus} + W_t \cdot \text{TransitionPenalty}$$

### 2. Quadratic Unconstrained Binary Optimization (QUBO)
Binary variables $x_{i, p} \in \{0, 1\}$ represent selecting phase $p$ at intersection $i$:

$$\min_{x \in \{0, 1\}^N} E(x) = \sum_{i} Q_{ii} x_i + \sum_{i < j} Q_{ij} x_i x_j + c$$

Where:
- **Linear terms $Q_{ii}$**: Traffic cost incurred if phase $i$ is activated.
- **Cross terms $Q_{ij}$**: Arterial coordination couplings between adjacent intersections (rewarding green waves).
- **One-Hot Constraint**: Enforcing exactly one active phase per intersection via penalty multiplier $P$:

$$P_{\text{one-hot}} = P \sum_{k} \left( \sum_{p \in \text{Phases}_k} x_{k, p} - 1 \right)^2$$

### 3. Ising Spin Hamiltonian Transformation
Using the mapping $x_i = \frac{1 - z_i}{2}$ where $z_i \in \{-1, +1\}$ are Pauli-$Z$ eigenvalues:

$$H_C = \sum_{i=1}^N h_i Z_i + \sum_{i < j} J_{ij} Z_i Z_j + c_{\text{Ising}} I$$

Where coefficients are computed without approximation:
$$h_i = -\frac{Q_{ii}}{2} - \sum_{j \neq i} \frac{Q_{ij}}{4}, \quad J_{ij} = \frac{Q_{ij}}{4}$$

### 4. QAOA Circuit Execution
The Quantum Approximate Optimization Algorithm prepares a parameterized quantum state over $p$ layers:

$$|\psi(\boldsymbol{\gamma}, \boldsymbol{\beta})\rangle = \prod_{l=1}^p \left( e^{-i \beta_l H_M} e^{-i \gamma_l H_C} \right) |+\rangle^{\otimes N}$$

- **Mixer Hamiltonian**: $H_M = \sum_{i=1}^N X_i$ (transverse field driving phase transitions).
- **Measurement**: Classical optimization updates $(\boldsymbol{\gamma}, \boldsymbol{\beta})$ using COBYLA until the expectation value $\langle \psi | H_C | \psi \rangle$ is minimized.

---

## 📂 Project Directory Structure

```text
Quantum-Traffic-Priority-Routing/
├── backend/
│   ├── app/
│   │   ├── adaptive/         # Adaptive signal control rules & cycle calculators
│   │   ├── api/              # FastAPI REST routers & WebSocket connection manager
│   │   ├── benchmark/        # Classical vs. Quantum comparison runners
│   │   ├── domain/           # Network graph, road link, intersection, and signal models
│   │   ├── emergency/        # Emergency vehicle dispatch & green wave service
│   │   ├── events/           # Dynamic incident handlers (accidents, closures, weather)
│   │   ├── metrics/          # Delay, throughput, fuel consumption, and CO2 models
│   │   ├── optimization/     # Hybrid quantum-classical decomposition & solvers
│   │   ├── quantum/          # Qiskit Aer QAOA, Ising converter, & ansatz circuits
│   │   ├── signals/qubo/     # QUBO builder, objective matrices, and solution decoders
│   │   └── simulation/       # Microscopic vehicle simulation engine & scenarios
│   └── tests/                # Comprehensive unit and integration test suite
├── frontend/
│   ├── app/
│   │   ├── layout.tsx        # Root layout with ThemeProvider and fonts
│   │   ├── page.tsx          # Standalone Hero Page (Q-TrafficX)
│   │   ├── console/page.tsx  # Full Operations Console
│   │   └── globals.css       # Vanilla CSS Design System (Dark & Light themes)
│   ├── components/
│   │   ├── dashboard/        # Header, ControlPanel, Sidebar
│   │   ├── emergency/        # EmergencyCorridorPanel
│   │   ├── events/           # EventInjectionModal, EventTimeline
│   │   ├── metrics/          # MetricCards, MetricTrends
│   │   ├── quantum/          # QuantumPanel, ClassicalComparison
│   │   ├── traffic/          # TrafficMap (Interactive Canvas), IntersectionModal
│   │   └── ui/               # LatticeLoader (LED matrix pulse animation)
│   └── public/               # Official Q-TrafficX brand assets and icons
├── docs/                     # Detailed architectural, API, benchmark, and judge documentation
├── Makefile                  # Automated build, test, lint, and run commands
└── README.md                 # Project master documentation
```

---

## 🚀 Quickstart & Installation

### Prerequisites
- **Python**: `3.11` or higher
- **Node.js**: `20.x` LTS or higher
- **npm**: `10.x` or higher

---

### Step 1: Clone & Configure

```bash
git clone https://github.com/karteyareddy/Qubits-Quantexa_Project.git
cd Qubits-Quantexa_Project

# Create virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Frontend dependencies
cd frontend
npm install
cd ..
```

---

### Step 2: Launch Backend API (:8000)

```bash
# In your terminal with virtual environment activated:
python -m uvicorn app.api.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```
*API Documentation & Swagger UI available at:* `http://127.0.0.1:8000/docs`

---

### Step 3: Launch Frontend UI (:3000)

```bash
# In a second terminal:
cd frontend
npm run dev
```

Open your browser at:
- **Standalone Hero Page**: [http://localhost:3000](http://localhost:3000)
- **Operations Console**: [http://localhost:3000/console](http://localhost:3000/console)

---

## 🎮 Interactive Demonstration Walkthrough

1. **Visit the Landing Page (`/`)**:
   - Experience the official **Q-TrafficX** branding with animated LED matrix indicators.
   - Click **`Launch Traffic Console →`** to enter operations.

2. **Run Micro-Simulation (`/console`)**:
   - Select a scenario from the dropdown: `Low Traffic (3 veh)` or `Congested Traffic (12 veh)`.
   - Use transport controls: Click **`▶ Start`**, **`⏸ Pause`**, **`⏭ Step 1s`**, or **`⏩ Skip +10s`**.
   - Adjust speed dynamically between **`1×`**, **`2×`**, and **`5×`**.

3. **Explore the Real-Time Road Network**:
   - Watch vehicles navigate across the 6 interconnected intersections with active headlights and dynamic speeds.
   - Observe signal heads cycling through Green, Yellow, and Red phases.
   - Click any intersection node ($I_1$ to $I_6$) to open the **Intersection Inspector** showing real-time approach queues.

4. **Trigger Hybrid QAOA Optimization**:
   - Click **`⚛ Optimize Now`**.
   - Watch the `LatticeLoader` solve the signal-control QUBO via Qiskit Aer simulation.
   - Review the **Hybrid Quantum Optimizer** card showing QUBO Energy, QAOA circuit execution time, and optimal phase selections.

5. **Simulate Dynamic Incidents**:
   - Click **`⚡ Inject Event`** to introduce a Road Accident, Lane Closure, Weather Slowdown, or Traffic Surge.
   - Watch the network adapt as vehicles slow down and queues adjust.

6. **Activate Emergency Green Wave Corridor**:
   - In the **Emergency Corridor** card, select an origin and destination (e.g. $I_1 \rightarrow I_6$) and click **`Activate Corridor`**.
   - Watch the ambulance route illuminate on the map as upcoming signals are preemptively held green for zero-delay passage.

7. **Review Real-Time Metrics & Benchmarks**:
   - Check the **Live Operational Analytics** cards for Average Wait Time, Network Throughput, Fuel Model, and $\text{CO}_2$ Footprint.
   - Inspect the **Classical vs. Hybrid Optimization** benchmark table comparing QAOA against the Classical Fixed-Time baseline.

8. **Toggle Theme**:
   - Click the theme toggle button in the header (`☀️ Light` / `🌙 Dark`) to experience both Cyber-Obsidian and Crisp Modern Light aesthetics.

---

## 🧪 Testing & Quality Gates

Run the automated test suite and type verification:

```bash
# Run backend unit and integration tests (pytest)
pytest backend/tests/unit backend/tests/integration -v

# Run Python linter (ruff)
ruff check backend

# Run Python static type analysis (mypy)
mypy backend/app

# Run Frontend production build (Next.js Turbopack)
cd frontend && npm run build
```

---

## ⚖️ Scientific Honesty & Technical Disclosure

- **Quantum Simulation**: All QAOA executions run on the state-of-the-art **Qiskit Aer Simulator** (`AerSimulator`), providing deterministic mathematical validation of quantum circuit behavior without claiming physical quantum supremacy.
- **Graceful Fallback**: When problem scale exceeds simulated qubit thresholds ($> 30$ qubits), the system automatically and transparently falls back to classical heuristic/greedy solvers with full logging.
- **Environmental Modeling**: Fuel consumption and carbon emissions are calculated using established engineering domain formulas (VT-Micro idle vs. cruise rates) labeled as prototype estimates.

---

## 📄 License & Acknowledgments

- **License**: MIT Open Source License.
- **Quantum Computing Stack**: Built with [Qiskit](https://qiskit.org/) & [Qiskit Aer](https://github.com/Qiskit/qiskit-aer).
- **Backend**: Built with [FastAPI](https://fastapi.tiangolo.com/) & [Pydantic](https://docs.pydantic.dev/).
- **Frontend**: Built with [Next.js](https://nextjs.org/) & [React](https://react.dev/).
- **Design & Branding**: Official **Q-TrafficX** identity — *Smarter Roads • Safer Cities • Greener Tomorrow*.
