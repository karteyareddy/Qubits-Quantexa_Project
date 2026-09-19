"""Automated end-to-end deployment smoke check script."""

import sys
import logging
from pathlib import Path

# Add backend directory to sys.path for direct script execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from fastapi.testclient import TestClient

from app.api.main import create_app
from app.benchmark.config import BenchmarkConfig
from app.benchmark.runner import BenchmarkRunner
from app.hardening import check_subsystem_health

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("smoke_test")


def run_deployment_smoke_check() -> bool:
    """Execute complete end-to-end system smoke check."""
    logger.info("=== Starting Quantum Traffic Priority Routing Deployment Smoke Check ===")

    # 1. Subsystem health check
    health_info = check_subsystem_health()
    logger.info("Subsystem Health Status: %s", health_info["status"])
    logger.info("Subsystems: %s", health_info["subsystems"])
    if health_info["status"] != "ok":
        logger.error("Subsystem health check failed!")
        return False

    # 2. FastAPI API Client startup
    app = create_app()
    client = TestClient(app)

    # 3. GET /health HTTP check
    res = client.get("/health")
    if res.status_code != 200 or res.json().get("status") != "ok":
        logger.error("GET /health failed: HTTP %s", res.status_code)
        return False
    logger.info("HTTP GET /health PASSED: %s", res.json())

    # 4. Create simulation session
    create_res = client.post(
        "/api/v1/simulations",
        json={"scenario_id": "low-traffic", "duration_seconds": 30.0, "seed": 42},
    )
    if create_res.status_code != 201:
        logger.error("Simulation creation failed: HTTP %s - %s", create_res.status_code, create_res.text)
        return False
    sim_id = create_res.json()["simulation_id"]
    logger.info("Created Simulation Session ID: %s", sim_id)

    # 5. Start simulation
    start_res = client.post(f"/api/v1/simulations/{sim_id}/start")
    if start_res.status_code != 200:
        logger.error("Simulation start failed: HTTP %s", start_res.status_code)
        return False
    logger.info("Simulation start PASSED")

    # 6. Step simulation
    step_res = client.post(f"/api/v1/simulations/{sim_id}/step", json={"step_seconds": 5.0})
    if step_res.status_code != 200 or step_res.json()["simulation_time_seconds"] != 5.0:
        logger.error("Simulation step failed: HTTP %s", step_res.status_code)
        return False
    logger.info("Simulation step PASSED: Time = 5.0s")

    # 7. Execute hybrid optimization
    opt_res = client.post(f"/api/v1/simulations/{sim_id}/optimize", json={})
    if opt_res.status_code != 200:
        logger.error("Hybrid optimization failed: HTTP %s - %s", opt_res.status_code, opt_res.text)
        return False
    opt_data = opt_res.json()
    logger.info("Hybrid Optimization PASSED: Solver = %s, Feasible = %s, Fallback = %s",
                opt_data.get("solver_name"), opt_data.get("is_feasible"), opt_data.get("fallback_used"))

    # 8. Inject dynamic event
    event_res = client.post(
        f"/api/v1/simulations/{sim_id}/events",
        json={
            "type": "congestion_spike",
            "edge_id": "I1->I2",
            "timestamp": 10.0,
            "duration": 15.0,
            "multiplier": 2.0,
        },
    )
    if event_res.status_code != 201:
        logger.error("Event injection failed: HTTP %s", event_res.status_code)
        return False
    logger.info("Dynamic event injection PASSED: Event ID = %s", event_res.json()["event_id"])

    # 9. Query emergency corridor status
    emergency_res = client.get(f"/api/v1/simulations/{sim_id}/emergency")
    if emergency_res.status_code != 200:
        logger.error("Emergency corridor query failed: HTTP %s", emergency_res.status_code)
        return False
    logger.info("Emergency corridor query PASSED")

    # 10. Fetch current metrics
    metrics_res = client.get(f"/api/v1/simulations/{sim_id}/metrics")
    if metrics_res.status_code != 200:
        logger.error("Metrics retrieval failed: HTTP %s", metrics_res.status_code)
        return False
    logger.info("Metrics retrieval PASSED: Total Vehicles = %s", metrics_res.json().get("total_vehicles"))

    # 11. Run Stage 16 benchmark smoke test
    logger.info("Running benchmark suite smoke check...")
    runner = BenchmarkRunner()
    bmk_config = BenchmarkConfig(scenario_id="low-traffic", duration_seconds=10.0, seed=42)
    comparison = runner.run_matched_comparison(bmk_config)
    if comparison.classical_result.status != "COMPLETED" or comparison.hybrid_result.status != "COMPLETED":
        logger.error("Benchmark suite smoke check failed! Status: classical=%s, hybrid=%s",
                     comparison.classical_result.status, comparison.hybrid_result.status)
        return False
    logger.info("Benchmark suite smoke check PASSED: Classical Runtime = %.3fs, Hybrid Runtime = %.3fs",
                comparison.classical_result.wall_clock_runtime_seconds, comparison.hybrid_result.wall_clock_runtime_seconds)

    # 12. Stop simulation session
    stop_res = client.post(f"/api/v1/simulations/{sim_id}/stop")
    if stop_res.status_code != 200:
        logger.error("Simulation stop failed: HTTP %s", stop_res.status_code)
        return False
    logger.info("Simulation stop PASSED")

    logger.info("=== Deployment Smoke Check COMPLETED SUCCESSFULLY ===")
    return True


if __name__ == "__main__":
    success = run_deployment_smoke_check()
    sys.exit(0 if success else 1)
