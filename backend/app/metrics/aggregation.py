"""Deterministic aggregation helpers for simulation outcomes."""

from collections.abc import Sequence

from app.domain.metrics import (
    EdgeTrafficMetrics,
    EmergencyMetrics,
    IntersectionApproachMetrics,
)
from app.domain.vehicle import Vehicle
from app.simulation.models import SimulationState


def spawned_vehicles(state: SimulationState) -> tuple[Vehicle, ...]:
    """Return spawned active and completed vehicles in stable ID order."""
    return tuple(
        sorted(
            (*state.active_vehicles, *state.completed_vehicles),
            key=lambda vehicle: vehicle.vehicle_id,
        )
    )


def metric_observations(
    final_state: SimulationState,
    observations: Sequence[SimulationState],
) -> tuple[SimulationState, ...]:
    """Normalize a trajectory and ensure its final state is represented once."""
    normalized = tuple(observations)
    if not normalized:
        return (final_state,)
    if normalized[-1] != final_state:
        return (*normalized, final_state)
    return normalized


def total_queue_length(state: SimulationState) -> int:
    return len(state.waiting_vehicle_ids)


def edge_metrics(state: SimulationState) -> tuple[EdgeTrafficMetrics, ...]:
    edge_ids = sorted(set(state.edge_occupancy) | set(state.edge_queues))
    return tuple(
        EdgeTrafficMetrics(
            edge_id=edge_id,
            occupancy=len(state.edge_occupancy.get(edge_id, ())),
            queue_length=len(state.edge_queues.get(edge_id, ())),
            waiting_vehicle_ids=state.edge_queues.get(edge_id, ()),
        )
        for edge_id in edge_ids
    )


def intersection_approach_metrics(
    state: SimulationState,
) -> tuple[IntersectionApproachMetrics, ...]:
    return tuple(
        IntersectionApproachMetrics(
            approach_id=approach_id,
            queue_length=len(vehicle_ids),
            waiting_vehicle_ids=vehicle_ids,
        )
        for approach_id, vehicle_ids in sorted(
            state.intersection_approach_queues.items()
        )
    )


def emergency_metrics(vehicles: Sequence[Vehicle]) -> EmergencyMetrics:
    emergency = tuple(vehicle for vehicle in vehicles if vehicle.is_emergency)
    completed = tuple(
        vehicle for vehicle in emergency if vehicle.completion_time_seconds is not None
    )
    total_waiting = sum(vehicle.waiting_time_seconds for vehicle in emergency)
    travel_times = tuple(
        vehicle.completion_time_seconds - vehicle.arrival_time_seconds
        for vehicle in completed
        if vehicle.completion_time_seconds is not None
    )
    return EmergencyMetrics(
        emergency_total=len(emergency),
        emergency_completed=len(completed),
        emergency_active=len(emergency) - len(completed),
        emergency_completion_rate=_safe_ratio(len(completed), len(emergency)),
        emergency_total_waiting_seconds=total_waiting,
        emergency_average_waiting_seconds=_safe_average(
            tuple(vehicle.waiting_time_seconds for vehicle in emergency)
        ),
        emergency_average_travel_seconds=_safe_average(travel_times),
    )


def safe_average(values: Sequence[float]) -> float:
    return _safe_average(values)


def safe_ratio(numerator: float, denominator: float) -> float:
    return _safe_ratio(numerator, denominator)


def _safe_average(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _safe_ratio(numerator: float, denominator: float) -> float:
    return float(numerator) / float(denominator) if denominator else 0.0
