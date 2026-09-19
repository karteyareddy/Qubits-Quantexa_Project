"""Dynamic event injection and history endpoints."""

import uuid

from fastapi import APIRouter, Depends

from app.api.dependencies import get_simulation_session
from app.api.schemas.events import (
    AccidentEventRequest,
    CongestionSpikeEventRequest,
    EmergencyArrivalEventRequest,
    EventInjectRequest,
    EventRecordResponse,
    RoadClosureEventRequest,
)
from app.api.session import SimulationSession
from app.events.models import (
    AccidentEvent,
    CongestionSpikeEvent,
    EmergencyArrivalEvent,
    RoadClosureEvent,
    TrafficEventBase,
)

events_router = APIRouter(prefix="/simulations", tags=["Events"])


@events_router.post("/{simulation_id}/events", response_model=EventRecordResponse, status_code=201)
async def inject_event(
    req: EventInjectRequest,
    session: SimulationSession = Depends(get_simulation_session),
) -> EventRecordResponse:
    """Inject a dynamic traffic event into an active simulation session."""
    async with session.lock:
        event_id = req.event_id or f"evt-{uuid.uuid4().hex[:6]}"
        event_obj: TrafficEventBase

        if isinstance(req, CongestionSpikeEventRequest):
            event_obj = CongestionSpikeEvent(
                event_id=event_id,
                starts_at_seconds=req.timestamp,
                edge_id=req.edge_id,
                additional_vehicle_count=max(1, int(req.multiplier * 2)),
                duration_seconds=req.duration,
            )
        elif isinstance(req, AccidentEventRequest):
            event_obj = AccidentEvent(
                event_id=event_id,
                starts_at_seconds=req.timestamp,
                edge_id=req.edge_id,
                capacity_factor=max(0.0, 1.0 - req.capacity_reduction),
                duration_seconds=req.duration,
            )
        elif isinstance(req, RoadClosureEventRequest):
            event_obj = RoadClosureEvent(
                event_id=event_id,
                starts_at_seconds=req.timestamp,
                edge_id=req.target,
                duration_seconds=req.duration,
            )
        elif isinstance(req, EmergencyArrivalEventRequest):
            event_obj = EmergencyArrivalEvent(
                event_id=event_id,
                starts_at_seconds=req.timestamp,
                vehicle_id=req.vehicle_id,
                origin=req.origin,
                destination=req.destination,
                priority=req.priority_weight,
            )
        else:
            raise TypeError("Unsupported event request payload")

        session.event_engine.scheduler.add_event(event_obj)

        return EventRecordResponse(
            event_id=event_obj.event_id,
            event_type=event_obj.event_type.value,
            timestamp=event_obj.timestamp,
            duration=event_obj.duration or 0.0,
            status="scheduled",
            target=event_obj.target,
            details={},
        )


@events_router.get("/{simulation_id}/events", response_model=list[EventRecordResponse])
def list_events(
    session: SimulationSession = Depends(get_simulation_session),
) -> list[EventRecordResponse]:
    """Retrieve all scheduled, active, and completed events for simulation."""
    res: list[EventRecordResponse] = []

    # Add processed/history event records
    for r in session.event_engine.history:
        res.append(
            EventRecordResponse(
                event_id=r.event_id,
                event_type=r.event_type.value,
                timestamp=r.starts_at_seconds,
                duration=r.duration_seconds or 0.0,
                status=r.status.value,
                target=r.target,
                details={},
            )
        )

    # Add currently scheduled events that haven't been processed yet
    history_ids = {r.event_id for r in session.event_engine.history}
    for ev in session.event_engine.scheduler._scheduled_events:
        if ev.event_id not in history_ids:
            res.append(
                EventRecordResponse(
                    event_id=ev.event_id,
                    event_type=ev.event_type.value,
                    timestamp=ev.timestamp,
                    duration=ev.duration or 0.0,
                    status="scheduled",
                    target=ev.target,
                    details={},
                )
            )

    return res
