"""Automated demo execution check script for hackathon presentation verification."""

import sys
import logging
from pathlib import Path

# Add backend directory to sys.path for direct script execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.demo.runner import DemoRunner
from app.demo.config import DemoConfig

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("demo_check")


def run_demo_check() -> bool:
    """Execute demo runner and verify presentation milestones and metrics."""
    logger.info("=== Starting Quantum Traffic Priority Routing Demo Verification ===")

    runner = DemoRunner()
    config = DemoConfig(seed=42, duration_seconds=60.0)

    try:
        result = runner.run_demo(config)

        logger.info("Demo ID: %s", result.demo_id)
        logger.info("Execution Status: %s", result.status)
        logger.info("Duration: %.1fs", result.duration_seconds)
        logger.info("Total Vehicles Spawned: %d", result.total_vehicles_spawned)
        logger.info("Total Vehicles Completed: %d", result.total_vehicles_completed)
        logger.info("Average Waiting Time: %.2fs", result.average_waiting_time_seconds)
        logger.info("Total CO2 Emitted: %.3f kg", result.total_co2_emitted_kg)
        logger.info("Optimizations Count: %d", result.optimizations_count)
        logger.info("Last Solver Used: %s", result.qaoa_solver_name)

        logger.info("--- Narrative Milestones Logged ---")
        for m in result.milestones:
            logger.info("  [%4.1fs] [%s] %s - %s", m.timestamp_seconds, m.subsystem.upper(), m.title, m.description)

        if result.status != "COMPLETED":
            logger.error("Demo check failed: Status is not COMPLETED!")
            return False

        if not result.milestones:
            logger.error("Demo check failed: No milestones were recorded!")
            return False

        if result.optimizations_count <= 0:
            logger.error("Demo check failed: No optimizations were executed!")
            return False

        logger.info("=== DEMO CHECK PASSED SUCCESSFULLY ===")
        return True
    except Exception as exc:
        logger.exception("Demo check failed with exception: %s", exc)
        return False


if __name__ == "__main__":
    success = run_demo_check()
    sys.exit(0 if success else 1)
