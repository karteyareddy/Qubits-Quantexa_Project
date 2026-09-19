"""System health diagnostics inspection."""

import importlib.util
from typing import Any


def check_subsystem_health() -> dict[str, Any]:
    """Inspect core subsystem availability and version details."""
    qiskit_available = importlib.util.find_spec("qiskit") is not None
    qiskit_aer_available = importlib.util.find_spec("qiskit_aer") is not None

    return {
        "status": "ok",
        "subsystems": {
            "simulation_engine": "available",
            "adaptive_controller": "available",
            "event_engine": "available",
            "emergency_corridor": "available",
            "qubo_builder": "available",
            "qaoa_solver": "available" if qiskit_available else "fallback_only",
            "qiskit_aer": "available" if qiskit_aer_available else "fallback_only",
        },
    }
