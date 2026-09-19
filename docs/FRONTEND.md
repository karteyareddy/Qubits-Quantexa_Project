# Next.js Interactive Traffic Dashboard (Stage 15)

## 1. Overview

The Stage 15 Next.js application (`frontend/`) provides an interactive urban traffic control center dashboard for the **Quantum-Enhanced Adaptive Urban Traffic Optimization** project.

It integrates seamlessly with the FastAPI REST + WebSocket application backend (`backend/app/api`), displaying real-time traffic density, signal phase states, hybrid QAOA optimization status, dynamic events log, and emergency green corridors.

```text
┌────────────────────────────────────────────────────────┐
│ Header (Time, Status, WebSocket, Scenario, QAOA Aer)   │
├────────────────────────────────────────────────────────┤
│ ControlPanel (Start, Pause, Step, Stop, Optimize, Event)│
├───────────────────┬────────────────────────────────────┤
│ Left Column       │ Right Column                       │
│ MetricCards       │ TrafficMap (6-Intersection SVG)   │
│ MetricTrends      │ IntersectionDetailModal            │
│ QuantumPanel      │ EmergencyCorridorPanel             │
│ ClassicalComp     │ EventTimeline                      │
└───────────────────┴────────────────────────────────────┘
```

---

## 2. Target Architecture & Component Hierarchy

```text
frontend/
├── app/
│   ├── page.tsx               # Primary dashboard layout
│   ├── layout.tsx             # Root layout & meta settings
│   └── globals.css            # Dark control center theme & utility styles
├── components/
│   ├── dashboard/
│   │   ├── Header.tsx         # Top application bar
│   │   └── ControlPanel.tsx   # Simulation lifecycle & optimization control bar
│   ├── traffic/
│   │   ├── TrafficMap.tsx     # 6-intersection SVG grid topology & vehicle markers
│   │   └── IntersectionDetailModal.tsx # Node detail inspection modal
│   ├── metrics/
│   │   ├── MetricCards.tsx    # Live KPI summary cards
│   │   └── MetricTrends.tsx   # Client-buffered sparkline charts
│   ├── quantum/
│   │   ├── QuantumPanel.tsx   # QAOA solver depth, QUBO energy, fallback status
│   │   └── ClassicalComparison.tsx # Side-by-side classical vs hybrid metrics
│   ├── emergency/
│   │   └── EmergencyCorridorPanel.tsx # Active emergency route & green windows
│   └── events/
│       ├── EventTimeline.tsx  # Dynamic event log timeline
│       └── EventInjectionModal.tsx # Modal form for event injection
├── lib/
│   ├── api.ts                 # Centralized REST client
│   ├── websocket.ts           # Auto-reconnecting WebSocket client
│   ├── types.ts               # Typed models matching FastAPI Pydantic schemas
│   └── formatters.ts          # Display value formatters
└── hooks/
    ├── useSimulationSocket.ts # WebSocket connection hook
    └── useDashboard.ts        # Primary state management hook
```

---

## 3. Key Features

### 3.1 Live 6-Intersection Traffic Grid (`TrafficMap.tsx`)
- Visualizes the 6-intersection grid ($I_1 \dots I_6$, 14 directed edges).
- Dynamic edge congestion styling (cyan/slate for low, amber for moderate, rose for high, dashed red for road closures).
- Active signal phase indicators ($\text{EW GREEN}$ / $\text{NS GREEN}$) and queue lengths per node.
- Animated vehicle markers and high-visibility pulse markers for emergency vehicles.
- Active emergency corridor route highlighting ($I_1 \Rightarrow I_2 \Rightarrow I_5 \Rightarrow I_6$).

### 3.2 Real-Time Control & QAOA Optimization
- **Simulation Control**: Initialize, Start, Pause, Step 1s, Stop.
- **Manual QAOA Trigger**: "Optimize Now" button invokes hybrid signal solver against current traffic state.
- **Quantum Solver Status**: Displays Solver Name, Backend (Qiskit Aer), QAOA Circuit Depth ($p=1$), QUBO Energy, and Feasibility.
- **Neutral Classical Comparison**: Side-by-side performance review without unsupported advantage claims.

### 3.3 Emergency Green Corridor & Dynamic Events
- **Emergency Corridor Panel**: Displays active vehicle ID, planned intersection sequence, and reserved signal green windows.
- **Dynamic Event Injection**: User-friendly form for Congestion Spikes, Accidents, Road Closures, and Emergency Vehicle arrivals.

---

## 4. Local Development

### Prerequisites
- Node.js 18+ & npm
- Python 3.10+ (for backend)

### Setup & Execution

1. **Start FastAPI Backend**:
   ```bash
   uvicorn backend.app.api.main:app --reload --port 8000
   ```

2. **Start Next.js Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Access Dashboard**:
   Navigate to `http://localhost:3000`.

---

## 5. Quality Verification

```bash
cd frontend
npm run lint
npm run build
```
