"""Integration tests for FastAPI REST routes."""

from app.api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_endpoint() -> None:
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_network_endpoint() -> None:
    res = client.get("/api/v1/network")
    assert res.status_code == 200
    data = res.json()
    assert len(data["intersections"]) == 6
    assert len(data["edges"]) == 14
    assert len(data["signalized_intersections"]) == 6


def test_scenarios_endpoint() -> None:
    res = client.get("/api/v1/scenarios")
    assert res.status_code == 200
    scenarios = res.json()
    assert len(scenarios) >= 3
    s_ids = {s["scenario_id"] for s in scenarios}
    assert "low-traffic" in s_ids
    assert "congested-traffic" in s_ids
    assert "emergency-vehicle" in s_ids
    emergency = next(s for s in scenarios if s["scenario_id"] == "emergency-vehicle")
    assert emergency["duration_seconds"] == 300.0


def test_simulation_lifecycle_rest() -> None:
    # 1. Create Simulation
    create_res = client.post(
        "/api/v1/simulations",
        json={"scenario_id": "low-traffic", "duration_seconds": 60.0, "seed": 42},
    )
    assert create_res.status_code == 201
    sim_data = create_res.json()
    sim_id = sim_data["simulation_id"]
    assert sim_data["status"] == "created"

    # 2. Get State
    state_res = client.get(f"/api/v1/simulations/{sim_id}")
    assert state_res.status_code == 200
    state = state_res.json()
    assert state["simulation_id"] == sim_id
    assert len(state["vehicles"]) == 3
    assert len(state["signals"]) == 6
    assert state["metrics"]["simulation_id"] == sim_id
    assert state["metrics"]["total_vehicles"] == 3
    assert state["latest_optimization"] is None

    # 3. Start
    start_res = client.post(f"/api/v1/simulations/{sim_id}/start")
    assert start_res.status_code == 200
    assert start_res.json()["status"] == "running"

    # 4. Step
    step_res = client.post(f"/api/v1/simulations/{sim_id}/step", json={"step_seconds": 5.0})
    assert step_res.status_code == 200
    stepped_state = step_res.json()
    assert stepped_state["simulation_time_seconds"] == 5.0
    assert stepped_state["metrics"]["simulation_time_seconds"] == 5.0
    assert stepped_state["latest_optimization"] is not None
    assert "solver_name" in stepped_state["latest_optimization"]

    # 5. Inject Event
    event_payload = {
        "type": "congestion_spike",
        "timestamp": 10.0,
        "edge_id": "I1->I2",
        "multiplier": 3.0,
        "duration": 20.0,
    }
    evt_res = client.post(f"/api/v1/simulations/{sim_id}/events", json=event_payload)
    assert evt_res.status_code == 201
    assert evt_res.json()["event_type"] in ["congestion", "congestion_spike"]

    # List Events
    events_list_res = client.get(f"/api/v1/simulations/{sim_id}/events")
    assert events_list_res.status_code == 200
    assert len(events_list_res.json()) >= 1

    # 6. Manual Optimization Trigger
    opt_res = client.post(f"/api/v1/simulations/{sim_id}/optimize", json={"apply_immediately": True})
    assert opt_res.status_code == 200
    opt_data = opt_res.json()
    assert "solver_name" in opt_data
    assert "is_feasible" in opt_data

    # 7. Get Metrics
    metrics_res = client.get(f"/api/v1/simulations/{sim_id}/metrics")
    assert metrics_res.status_code == 200
    m = metrics_res.json()
    assert m["total_vehicles"] >= 1

    # 8. Pause
    pause_res = client.post(f"/api/v1/simulations/{sim_id}/pause")
    assert pause_res.status_code == 200
    assert pause_res.json()["status"] == "paused"

    # 9. Stop
    stop_res = client.post(f"/api/v1/simulations/{sim_id}/stop")
    assert stop_res.status_code == 200
    assert stop_res.json()["status"] == "completed"


def test_nonexistent_simulation_404() -> None:
    res = client.get("/api/v1/simulations/nonexistent-sim-999")
    assert res.status_code == 404
    data = res.json()
    assert data["error"]["code"] == "SIMULATION_NOT_FOUND"


def test_emergency_corridor_api() -> None:
    # Create emergency scenario simulation
    c_res = client.post(
        "/api/v1/simulations",
        json={"scenario_id": "emergency-vehicle", "duration_seconds": 60.0},
    )
    assert c_res.status_code == 201
    sim_id = c_res.json()["simulation_id"]

    # Step to t=10 where emergency vehicle arrives
    client.post(f"/api/v1/simulations/{sim_id}/step", json={"step_seconds": 10.0})

    state_res = client.get(f"/api/v1/simulations/{sim_id}")
    state_corridors = state_res.json()["emergency_corridors"]
    assert len(state_corridors) == 1
    assert state_corridors[0]["vehicle_id"] == "emergency-001"
    assert state_corridors[0]["status"] == "active"
    assert len(state_corridors[0]["green_windows"]) >= 1

    # GET emergency corridors
    em_res = client.get(f"/api/v1/simulations/{sim_id}/emergency")
    assert em_res.status_code == 200
    corridors = em_res.json()
    assert isinstance(corridors, list)

    # Activate emergency corridor manually
    act_res = client.post(f"/api/v1/simulations/{sim_id}/emergency/emergency-001/activate")
    assert act_res.status_code == 200
    corridor_data = act_res.json()
    assert corridor_data["vehicle_id"] == "emergency-001"
    assert corridor_data["status"] in ["planned", "active"]


def test_injected_emergency_extends_short_session_horizon() -> None:
    create_res = client.post(
        "/api/v1/simulations",
        json={
            "scenario_id": "low-traffic",
            "duration_seconds": 20.0,
            "adaptive_enabled": False,
        },
    )
    sim_id = create_res.json()["simulation_id"]
    client.post(f"/api/v1/simulations/{sim_id}/start")

    event_res = client.post(
        f"/api/v1/simulations/{sim_id}/events",
        json={
            "type": "emergency_arrival",
            "timestamp": 1.0,
            "vehicle_id": "emergency-horizon-test",
            "origin": "I1",
            "destination": "I6",
            "priority_weight": 20,
        },
    )
    assert event_res.status_code == 201

    step_res = client.post(
        f"/api/v1/simulations/{sim_id}/step",
        json={"step_seconds": 150.0},
    )
    assert step_res.status_code == 200
    state = step_res.json()
    emergency = next(
        vehicle
        for vehicle in state["vehicles"]
        if vehicle["vehicle_id"] == "emergency-horizon-test"
    )
    assert emergency["has_arrived"] is True
    assert state["emergency_corridors"][0]["status"] == "completed"
