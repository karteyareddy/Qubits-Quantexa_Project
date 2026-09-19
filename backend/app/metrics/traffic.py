"""Traffic-performance metrics calculated from simulation outcomes."""

from collections.abc import Sequence

from app.domain.metrics import TrafficMetrics, VehicleMetrics
from app.domain.vehicle import Vehicle
from app.metrics.aggregation import (
    edge_metrics,
    intersection_approach_metrics,
    metric_observations,
    safe_average,
    safe_ratio,
    spawned_vehicles,
    total_queue_length,
)
from app.simulation.models import SimulationState


def calculate_traffic_metrics(
    final_state: SimulationState,
    *,
    observations: Sequence[SimulationState] = (),
) -> TrafficMetrics:
    """Calculate controller-independent traffic outcomes.

    Waiting averages cover all spawned vehicles. Travel averages cover only
    completed vehicles and use completion time minus scheduled arrival time.
    """
    vehicles = spawned_vehicles(final_state)
    completed = tuple(
        vehicle for vehicle in vehicles if vehicle.completion_time_seconds is not None
    )
    vehicle_results = tuple(_vehicle_metrics(vehicle) for vehicle in vehicles)
    waiting_times = tuple(vehicle.waiting_time_seconds for vehicle in vehicles)
    travel_times = tuple(
        result.travel_time_seconds
        for result in vehicle_results
        if result.travel_time_seconds is not None
    )
    queue_lengths = tuple(
        total_queue_length(state)
        for state in metric_observations(final_state, observations)
    )
    duration = final_state.simulation_time_seconds
    completed_count = len(completed)
    total_count = len(vehicles)
    return TrafficMetrics(
        simulation_duration_seconds=duration,
        total_vehicles=total_count,
        completed_vehicles=completed_count,
        active_vehicles=total_count - completed_count,
        completion_rate=safe_ratio(completed_count, total_count),
        throughput=completed_count,
        throughput_per_minute=(completed_count * 60.0 / duration if duration else 0.0),
        total_waiting_seconds=sum(waiting_times),
        average_waiting_seconds=safe_average(waiting_times),
        max_waiting_seconds=max(waiting_times, default=0.0),
        average_travel_seconds=safe_average(travel_times),
        max_travel_seconds=max(travel_times, default=0.0),
        max_queue_length=max(queue_lengths, default=0),
        final_queue_length=total_queue_length(final_state),
        average_queue_length=safe_average(queue_lengths),
        per_vehicle=vehicle_results,
        edges=edge_metrics(final_state),
        intersection_approaches=intersection_approach_metrics(final_state),
    )


def _vehicle_metrics(vehicle: Vehicle) -> VehicleMetrics:
    completed = vehicle.completion_time_seconds is not None
    travel_time = None
    if vehicle.completion_time_seconds is not None:
        travel_time = vehicle.completion_time_seconds - vehicle.arrival_time_seconds
    return VehicleMetrics(
        vehicle_id=vehicle.vehicle_id,
        completed=completed,
        travel_time_seconds=travel_time,
        waiting_time_seconds=vehicle.waiting_time_seconds,
        emergency=vehicle.is_emergency,
    )
