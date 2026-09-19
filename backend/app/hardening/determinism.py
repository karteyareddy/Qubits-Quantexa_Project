"""Determinism and seed propagation helpers."""

import hashlib
import random

from app.simulation.models import SimulationState


def seed_all(seed: int) -> None:
    """Seed Python random and NumPy random generators deterministically."""
    random.seed(seed)
    try:
        import numpy as np

        np.random.seed(seed)
    except ImportError:
        pass


def compute_state_trajectory_hash(observations: list[SimulationState]) -> str:
    """Compute deterministic SHA-256 fingerprint of simulation trajectory observations."""
    hasher = hashlib.sha256()

    for obs in observations:
        t_str = f"{obs.simulation_time_seconds:.3f}"
        veh_str = ",".join(
            f"{v.vehicle_id}:{v.current_edge_id or 'NONE'}:{v.position_on_edge:.3f}"
            for v in sorted(obs.active_vehicles, key=lambda item: item.vehicle_id)
        )
        completed_count = len(obs.completed_vehicles)
        line = f"T={t_str}|V={veh_str}|C={completed_count}\n"
        hasher.update(line.encode("utf-8"))

    return hasher.hexdigest()


def verify_simulation_equivalence(
    observations_a: list[SimulationState], observations_b: list[SimulationState]
) -> bool:
    """Verify exact equivalence of two simulation trajectory observations."""
    hash_a = compute_state_trajectory_hash(observations_a)
    hash_b = compute_state_trajectory_hash(observations_b)
    return hash_a == hash_b
