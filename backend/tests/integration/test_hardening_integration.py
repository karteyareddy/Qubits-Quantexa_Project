"""Integration tests for Stage 17 Hardening & Reliability."""

import asyncio

import pytest
from app.api.main import create_app
from app.api.session import session_manager
from fastapi.testclient import TestClient


@pytest.fixture
def api_client() -> TestClient:
    app = create_app()
    return TestClient(app)


def test_health_check_endpoint(api_client: TestClient) -> None:
    response = api_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "subsystems" in data


def test_api_resource_limit_rejection(api_client: TestClient) -> None:
    # Attempt creating simulation with excessive duration (99999 seconds)
    response = api_client.post(
        "/api/v1/simulations",
        json={
            "scenario_id": "low-traffic",
            "duration_seconds": 99999.0,
            "seed": 42,
        },
    )
    assert response.status_code == 400
    error_payload = response.json()
    assert "error" in error_payload
    assert error_payload["error"]["code"] in ("RESOURCE_LIMIT_EXCEEDED", "VALIDATION_ERROR")


def test_simulation_session_concurrency(api_client: TestClient) -> None:
    response = api_client.post(
        "/api/v1/simulations",
        json={
            "scenario_id": "low-traffic",
            "duration_seconds": 60.0,
            "seed": 42,
        },
    )
    assert response.status_code == 201
    sim_id = response.json()["simulation_id"]

    session = session_manager.get_session(sim_id)

    # Test concurrent async steps
    async def concurrent_step() -> None:
        await session.step(step_seconds=1.0)

    async def run_concurrent_steps() -> None:
        await asyncio.gather(
            concurrent_step(),
            concurrent_step(),
            concurrent_step(),
        )

    asyncio.run(run_concurrent_steps())

    state = session.get_state_snapshot()
    assert state["simulation_time_seconds"] > 0.0


def test_full_scenario_lifecycle_smoke(api_client: TestClient) -> None:
    # 1. Create simulation
    create_res = api_client.post(
        "/api/v1/simulations",
        json={
            "scenario_id": "low-traffic",
            "duration_seconds": 30.0,
            "seed": 42,
        },
    )
    assert create_res.status_code == 201
    sim_id = create_res.json()["simulation_id"]

    # 2. Start simulation
    start_res = api_client.post(f"/api/v1/simulations/{sim_id}/start")
    assert start_res.status_code == 200

    # 3. Step simulation
    step_res = api_client.post(f"/api/v1/simulations/{sim_id}/step", json={"step_seconds": 5.0})
    assert step_res.status_code == 200
    assert step_res.json()["simulation_time_seconds"] == 5.0

    # 4. Inject dynamic event
    event_res = api_client.post(
        f"/api/v1/simulations/{sim_id}/events",
        json={
            "type": "congestion_spike",
            "edge_id": "I1->I2",
            "timestamp": 10.0,
            "duration": 15.0,
            "multiplier": 2.0,
        },
    )
    assert event_res.status_code == 201

    # 5. Fetch emergency corridors status
    emergency_res = api_client.get(f"/api/v1/simulations/{sim_id}/emergency")
    assert emergency_res.status_code == 200

    # 6. Step to advance time
    step_res2 = api_client.post(f"/api/v1/simulations/{sim_id}/step", json={"step_seconds": 10.0})
    assert step_res2.status_code == 200

    # 7. Fetch metrics
    metrics_res = api_client.get(f"/api/v1/simulations/{sim_id}/metrics")
    assert metrics_res.status_code == 200
    assert "average_travel_time_seconds" in metrics_res.json()

    # 8. Stop simulation
    stop_res = api_client.post(f"/api/v1/simulations/{sim_id}/stop")
    assert stop_res.status_code == 200
