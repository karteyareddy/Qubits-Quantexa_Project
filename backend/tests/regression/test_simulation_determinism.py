"""Regression proof for deterministic Stage 4 simulation trajectories."""

from app.simulation.engine import TrafficSimulation
from app.simulation.scenarios import congested_traffic_scenario


def test_same_scenario_produces_identical_sixty_second_trajectory() -> None:
    first = _trajectory()
    second = _trajectory()

    assert first == second


def _trajectory() -> tuple[dict[str, object], ...]:
    simulation = TrafficSimulation(congested_traffic_scenario(seed=42))
    snapshots: list[dict[str, object]] = []
    for _ in range(60):
        snapshots.append(simulation.step().model_dump(mode="json"))
    return tuple(snapshots)
