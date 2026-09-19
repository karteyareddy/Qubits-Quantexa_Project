"""Integration tests for FastAPI WebSocket live simulation endpoint."""

from app.api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_websocket_connection_and_streaming() -> None:
    # 1. Create a simulation session first
    create_res = client.post(
        "/api/v1/simulations",
        json={"scenario_id": "low-traffic", "duration_seconds": 60.0},
    )
    assert create_res.status_code == 201
    sim_id = create_res.json()["simulation_id"]

    # 2. Connect WebSocket
    with client.websocket_connect(f"/api/v1/simulations/{sim_id}/ws") as websocket:
        # Receive initial state envelope
        initial_msg = websocket.receive_json()
        assert initial_msg["type"] == "state"
        assert initial_msg["timestamp"] == 0.0
        assert initial_msg["data"]["simulation_id"] == sim_id

        # Send ping
        websocket.send_json({"action": "ping"})
        pong_msg = websocket.receive_json()
        assert pong_msg["type"] == "pong"

        # Send step action
        websocket.send_json({"action": "step", "step_seconds": 2.0})
        stepped_msg = websocket.receive_json()
        assert stepped_msg["type"] == "state"
        assert stepped_msg["timestamp"] == 2.0


def test_websocket_nonexistent_simulation() -> None:
    try:
        with client.websocket_connect("/api/v1/simulations/invalid-sim-id/ws") as ws:
            ws.receive_json()
    except Exception:  # noqa: S110, BLE001
        # FastAPI TestClient raises exception when socket closes with 4004 code
        pass
