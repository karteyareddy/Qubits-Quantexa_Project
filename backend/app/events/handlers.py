"""Traffic event effect handlers."""

from typing import Any

from app.domain.vehicle import EmergencySubtype, Vehicle, VehicleState, VehicleType
from app.events.models import (
    AccidentEvent,
    CongestionSpikeEvent,
    EmergencyArrivalEvent,
    EventRecord,
    EventStatus,
    RoadClosureEvent,
    TrafficEventBase,
)
from app.routing.routes import generate_candidate_routes
from app.simulation.engine import TrafficSimulation
from app.simulation.state import build_simulation_state


class EventHandlerError(Exception):
    """Raised when an event handler fails to apply an event."""


def apply_event(
    event: TrafficEventBase,
    simulation: TrafficSimulation,
    active_effects: dict[str, dict[str, Any]],
) -> EventRecord:
    """Dispatch event to its specific handler based on event type."""
    current_time = simulation.state.simulation_time_seconds

    try:
        if isinstance(event, CongestionSpikeEvent):
            record = _apply_congestion_spike(event, simulation, current_time)
        elif isinstance(event, AccidentEvent):
            record = _apply_accident(event, simulation, active_effects, current_time)
        elif isinstance(event, RoadClosureEvent):
            record = _apply_road_closure(event, simulation, active_effects, current_time)
        elif isinstance(event, EmergencyArrivalEvent):
            record = _apply_emergency_arrival(event, simulation, current_time)
        else:
            raise EventHandlerError(f"Unsupported event type: {type(event)}")

        return record
    except Exception as exc:
        if isinstance(exc, EventHandlerError):
            raise
        return EventRecord(
            event_id=event.event_id,
            event_type=event.event_type,
            starts_at_seconds=event.starts_at_seconds,
            duration_seconds=event.duration_seconds,
            applied_at_seconds=current_time,
            target=event.target,
            status=EventStatus.FAILED,
            failure_reason=str(exc),
        )


def _apply_congestion_spike(
    event: CongestionSpikeEvent,
    simulation: TrafficSimulation,
    current_time: float,
) -> EventRecord:
    target_edge_id = event.edge_id
    edge_map = {e.edge_id: e for e in simulation.scenario.network.edges}
    if target_edge_id not in edge_map:
        raise EventHandlerError(f"Target edge '{target_edge_id}' not found in network.")

    target_edge = edge_map[target_edge_id]
    origin = target_edge.source
    destination = target_edge.target

    routes = generate_candidate_routes(
        simulation.scenario.network, origin, destination, max_candidates=1
    )
    primary_route = routes[0]

    new_vehicles: list[Vehicle] = []
    for i in range(event.additional_vehicle_count):
        veh_id = f"congestion_{event.event_id}_{i+1}"
        v = Vehicle(
            vehicle_id=veh_id,
            vehicle_type=VehicleType.REGULAR,
            origin=origin,
            destination=destination,
            route=primary_route,
            candidate_routes=routes,
            arrival_time_seconds=current_time,
            state=VehicleState.PENDING,
        )
        new_vehicles.append(v)

    updated_pending = tuple(simulation.state.pending_vehicles) + tuple(new_vehicles)
    simulation._state = build_simulation_state(
        simulation_time_seconds=current_time,
        network=simulation.scenario.network,
        pending_vehicles=updated_pending,
        active_vehicles=simulation.state.active_vehicles,
        completed_vehicles=simulation.state.completed_vehicles,
    )

    duration = event.duration_seconds
    is_active = duration is not None and duration > 0
    return EventRecord(
        event_id=event.event_id,
        event_type=event.event_type,
        starts_at_seconds=event.starts_at_seconds,
        duration_seconds=duration,
        applied_at_seconds=current_time,
        expired_at_seconds=current_time + duration if duration else current_time,
        target=event.edge_id,
        status=EventStatus.ACTIVE if is_active else EventStatus.RESOLVED,
        metadata={"added_vehicles": event.additional_vehicle_count},
    )


def _apply_accident(
    event: AccidentEvent,
    simulation: TrafficSimulation,
    active_effects: dict[str, dict[str, Any]],
    current_time: float,
) -> EventRecord:
    target_edge_id = event.edge_id
    edge_map = {e.edge_id: e for e in simulation.scenario.network.edges}
    if target_edge_id not in edge_map:
        raise EventHandlerError(f"Target edge '{target_edge_id}' not found in network.")

    edge = edge_map[target_edge_id]
    original_capacity = edge.capacity
    reduced_capacity = max(1.0, original_capacity * event.capacity_factor)

    active_effects[event.event_id] = {
        "type": "accident",
        "edge_id": target_edge_id,
        "original_capacity": original_capacity,
    }

    # Update edge capacity in simulation network
    edge.capacity = reduced_capacity

    duration = event.duration_seconds or 0.0
    return EventRecord(
        event_id=event.event_id,
        event_type=event.event_type,
        starts_at_seconds=event.starts_at_seconds,
        duration_seconds=event.duration_seconds,
        applied_at_seconds=current_time,
        expired_at_seconds=current_time + duration,
        target=event.edge_id,
        status=EventStatus.ACTIVE,
        metadata={
            "original_capacity": original_capacity,
            "reduced_capacity": reduced_capacity,
            "severity": event.severity,
        },
    )


def _apply_road_closure(
    event: RoadClosureEvent,
    simulation: TrafficSimulation,
    active_effects: dict[str, dict[str, Any]],
    current_time: float,
) -> EventRecord:
    target_edge_id = event.edge_id
    edge_map = {e.edge_id: e for e in simulation.scenario.network.edges}
    if target_edge_id not in edge_map:
        raise EventHandlerError(f"Target edge '{target_edge_id}' not found in network.")

    edge = edge_map[target_edge_id]
    active_effects[event.event_id] = {
        "type": "road_closure",
        "edge_id": target_edge_id,
    }

    edge.closed = True

    duration = event.duration_seconds or 0.0
    return EventRecord(
        event_id=event.event_id,
        event_type=event.event_type,
        starts_at_seconds=event.starts_at_seconds,
        duration_seconds=event.duration_seconds,
        applied_at_seconds=current_time,
        expired_at_seconds=current_time + duration,
        target=event.edge_id,
        status=EventStatus.ACTIVE,
    )


def _apply_emergency_arrival(
    event: EmergencyArrivalEvent,
    simulation: TrafficSimulation,
    current_time: float,
) -> EventRecord:
    routes = generate_candidate_routes(
        simulation.scenario.network, event.origin, event.destination, max_candidates=3
    )

    emergency_veh = Vehicle(
        vehicle_id=event.vehicle_id,
        vehicle_type=VehicleType.EMERGENCY,
        is_emergency=True,
        emergency_subtype=EmergencySubtype.AMBULANCE,
        origin=event.origin,
        destination=event.destination,
        route=routes[0],
        candidate_routes=routes,
        priority_weight=event.priority,
        arrival_time_seconds=current_time,
        state=VehicleState.PENDING,
    )

    updated_pending = tuple(simulation.state.pending_vehicles) + (emergency_veh,)
    simulation._state = build_simulation_state(
        simulation_time_seconds=current_time,
        network=simulation.scenario.network,
        pending_vehicles=updated_pending,
        active_vehicles=simulation.state.active_vehicles,
        completed_vehicles=simulation.state.completed_vehicles,
    )

    duration = event.duration_seconds
    is_active = duration is not None and duration > 0
    return EventRecord(
        event_id=event.event_id,
        event_type=event.event_type,
        starts_at_seconds=event.starts_at_seconds,
        duration_seconds=duration,
        applied_at_seconds=current_time,
        expired_at_seconds=current_time + duration if duration else current_time,
        target=event.origin,
        status=EventStatus.ACTIVE if is_active else EventStatus.RESOLVED,
        metadata={"vehicle_id": event.vehicle_id, "priority": event.priority},
    )


def restore_event_effect(
    event_id: str,
    simulation: TrafficSimulation,
    active_effects: dict[str, dict[str, Any]],
) -> None:
    """Restore state modified by an active event upon its expiry."""
    if event_id not in active_effects:
        return

    effect = active_effects.pop(event_id)
    edge_map = {e.edge_id: e for e in simulation.scenario.network.edges}

    if effect["type"] == "accident":
        edge_id = effect["edge_id"]
        if edge_id in edge_map:
            edge_map[edge_id].capacity = effect["original_capacity"]
    elif effect["type"] == "road_closure":
        edge_id = effect["edge_id"]
        if edge_id in edge_map:
            edge_map[edge_id].closed = False
