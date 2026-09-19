"""Emergency Green Corridor status and activation endpoints."""

from fastapi import APIRouter, Depends

from app.api.dependencies import get_simulation_session
from app.api.errors import APIException
from app.api.schemas.emergency import (
    EmergencyCorridorResponse,
    GreenWindowResponse,
)
from app.api.session import SimulationSession
from app.emergency.corridor import EmergencyCorridorPlanner
from app.emergency.models import CorridorStatus

emergency_router = APIRouter(prefix="/simulations", tags=["Emergency Corridor"])


@emergency_router.get(
    "/{simulation_id}/emergency", response_model=list[EmergencyCorridorResponse]
)
def get_emergency_corridors(
    session: SimulationSession = Depends(get_simulation_session),
) -> list[EmergencyCorridorResponse]:
    """Retrieve all emergency green corridors for active simulation session."""
    corridors = list(session.emergency_service.corridor_history)
    responses: list[EmergencyCorridorResponse] = []

    for c in corridors:
        gw_list = [
            GreenWindowResponse(
                intersection_id=res.intersection_id,
                arrival_time_seconds=res.arrival_time_seconds,
                window_start_seconds=res.green_window_start,
                window_end_seconds=res.green_window_end,
                incoming_approach=res.incoming_edge_id,
                outgoing_approach=res.outgoing_edge_id,
                required_phase=res.required_phase.value,
            )
            for res in c.intersections
        ]

        responses.append(
            EmergencyCorridorResponse(
                corridor_id=c.corridor_id,
                vehicle_id=c.vehicle_id,
                route=list(c.route.edge_ids),
                intersections=[res.intersection_id for res in c.intersections],
                status=c.status.value,
                created_at_seconds=c.created_at_seconds,
                activated_at_seconds=c.activated_at_seconds,
                released_at_seconds=c.released_at_seconds,
                green_windows=gw_list,
                failure_reason=c.failure_reason,
            )
        )

    return responses


@emergency_router.post(
    "/{simulation_id}/emergency/{vehicle_id}/activate",
    response_model=EmergencyCorridorResponse,
)
async def activate_emergency_corridor(
    vehicle_id: str,
    session: SimulationSession = Depends(get_simulation_session),
) -> EmergencyCorridorResponse:
    """Explicitly activate or rebuild emergency corridor for a vehicle."""
    async with session.lock:
        all_vehicles = list(session.sim.state.active_vehicles) + list(session.sim.state.pending_vehicles) + list(session.sim.state.completed_vehicles)
        vehicle = next((v for v in all_vehicles if v.vehicle_id == vehicle_id), None)
        if vehicle is None:
            raise APIException(
                status_code=404,
                code="VEHICLE_NOT_FOUND",
                message=f"Vehicle '{vehicle_id}' not found in simulation.",
            )

        if not vehicle.is_emergency:
            raise APIException(
                status_code=400,
                code="NOT_EMERGENCY_VEHICLE",
                message=f"Vehicle '{vehicle_id}' is not an emergency vehicle.",
            )

        current_time = session.sim.state.simulation_time_seconds
        corridor = EmergencyCorridorPlanner.plan_corridor(
            vehicle=vehicle,
            network=session.sim.scenario.network,
            current_time=current_time,
            config=session.emergency_service.config,
        )
        if corridor.status == CorridorStatus.PLANNED:
            corridor = corridor.model_copy(
                update={"status": CorridorStatus.ACTIVE, "activated_at_seconds": current_time}
            )
        session.emergency_service._corridors[corridor.corridor_id] = corridor
        session.emergency_service._history.append(corridor)

        gw_list = [
            GreenWindowResponse(
                intersection_id=res.intersection_id,
                arrival_time_seconds=res.arrival_time_seconds,
                window_start_seconds=res.green_window_start,
                window_end_seconds=res.green_window_end,
                incoming_approach=res.incoming_edge_id,
                outgoing_approach=res.outgoing_edge_id,
                required_phase=res.required_phase.value,
            )
            for res in corridor.intersections
        ]

        return EmergencyCorridorResponse(
            corridor_id=corridor.corridor_id,
            vehicle_id=corridor.vehicle_id,
            route=list(corridor.route.edge_ids),
            intersections=[res.intersection_id for res in corridor.intersections],
            status=corridor.status.value,
            created_at_seconds=corridor.created_at_seconds,
            activated_at_seconds=corridor.activated_at_seconds,
            released_at_seconds=corridor.released_at_seconds,
            green_windows=gw_list,
            failure_reason=corridor.failure_reason,
        )
