"""Simulation snapshot construction from vehicle runtime state."""

from collections import defaultdict

from app.domain.network import Network
from app.domain.vehicle import Vehicle, VehicleState
from app.simulation.models import SimulationCounts, SimulationState


def build_simulation_state(
    *,
    simulation_time_seconds: float,
    network: Network,
    pending_vehicles: tuple[Vehicle, ...],
    active_vehicles: tuple[Vehicle, ...],
    completed_vehicles: tuple[Vehicle, ...],
) -> SimulationState:
    """Build deterministic occupancy and queue indexes for a snapshot."""
    edge_occupancy: dict[str, list[str]] = defaultdict(list)
    edge_queues: dict[str, list[str]] = defaultdict(list)
    approach_queues: dict[str, list[str]] = defaultdict(list)
    waiting_ids: list[str] = []

    for vehicle in sorted(active_vehicles, key=lambda item: item.vehicle_id):
        if vehicle.current_edge_id is not None:
            edge_occupancy[vehicle.current_edge_id].append(vehicle.vehicle_id)
        if vehicle.state is not VehicleState.WAITING:
            continue
        waiting_ids.append(vehicle.vehicle_id)
        next_edge_id = _next_edge_id(vehicle)
        if next_edge_id is not None:
            edge_queues[next_edge_id].append(vehicle.vehicle_id)
        approach_id = vehicle.current_edge_id or f"origin:{vehicle.current_node_id}"
        approach_queues[approach_id].append(vehicle.vehicle_id)

    occupancy = {
        edge.edge_id: tuple(edge_occupancy.get(edge.edge_id, ())) for edge in network.edges
    }
    queues = {
        edge.edge_id: tuple(edge_queues.get(edge.edge_id, ())) for edge in network.edges
    }
    return SimulationState(
        simulation_time_seconds=simulation_time_seconds,
        pending_vehicles=tuple(
            sorted(pending_vehicles, key=lambda item: (item.arrival_time_seconds, item.vehicle_id))
        ),
        active_vehicles=tuple(sorted(active_vehicles, key=lambda item: item.vehicle_id)),
        completed_vehicles=tuple(sorted(completed_vehicles, key=lambda item: item.vehicle_id)),
        waiting_vehicle_ids=tuple(waiting_ids),
        edge_occupancy=occupancy,
        edge_queues=queues,
        intersection_approach_queues={
            key: tuple(value) for key, value in sorted(approach_queues.items())
        },
        counts=SimulationCounts(
            pending=len(pending_vehicles),
            active=len(active_vehicles),
            completed=len(completed_vehicles),
            waiting=len(waiting_ids),
            throughput=len(completed_vehicles),
        ),
    )


def _next_edge_id(vehicle: Vehicle) -> str | None:
    if vehicle.route is None or not vehicle.route.edge_ids:
        return None
    if vehicle.current_edge_id is None:
        return vehicle.route.edge_ids[0]
    next_index = vehicle.current_route_index + 1
    if next_index >= len(vehicle.route.edge_ids):
        return None
    return vehicle.route.edge_ids[next_index]
