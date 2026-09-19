"""EventScheduler sorting events deterministically and managing lifecycles."""

from collections.abc import Sequence

from app.domain.event import EventStatus, EventType
from app.events.models import EventRecord, TrafficEventBase


def _event_priority_rank(event_type: EventType) -> int:
    """Return tie-breaking priority rank for events occurring at the exact same timestamp."""
    mapping = {
        EventType.ROAD_CLOSURE: 1,
        EventType.ACCIDENT: 2,
        EventType.CONGESTION: 3,
        EventType.EMERGENCY_ARRIVAL: 4,
    }
    return mapping.get(event_type, 99)


class EventScheduler:
    """Manages scheduled events with deterministic ordering and idempotency."""

    def __init__(self, events: Sequence[TrafficEventBase] = ()) -> None:
        self._scheduled_events: list[TrafficEventBase] = list(events)
        self._sort_events()
        self._applied_event_ids: set[str] = set()
        self._active_records: dict[str, EventRecord] = {}
        self._event_history: dict[str, EventRecord] = {}

        # Initialize event records
        for e in self._scheduled_events:
            target = getattr(e, "edge_id", getattr(e, "vehicle_id", "network"))
            rec = EventRecord(
                event_id=e.event_id,
                event_type=e.event_type,
                starts_at_seconds=e.starts_at_seconds,
                duration_seconds=e.duration_seconds,
                status=EventStatus.SCHEDULED,
                target=target,
            )
            self._event_history[e.event_id] = rec

    def _sort_events(self) -> None:
        """Sort scheduled events deterministically."""
        self._scheduled_events.sort(
            key=lambda e: (e.starts_at_seconds, _event_priority_rank(e.event_type), e.event_id)
        )

    def add_event(self, event: TrafficEventBase) -> None:
        """Add an event to the schedule."""
        if any(e.event_id == event.event_id for e in self._scheduled_events):
            raise ValueError(f"Duplicate event_id '{event.event_id}' registered in scheduler")
        self._scheduled_events.append(event)
        self._sort_events()

    def add_events(self, events: Sequence[TrafficEventBase]) -> None:
        """Add multiple events to the schedule."""
        for e in events:
            self.add_event(e)

    def is_processed(self, event_id: str) -> bool:
        """Check if an event ID has already been applied."""
        return event_id in self._applied_event_ids

    def mark_processed(self, event_id: str) -> None:
        """Mark an event ID as applied/processed."""
        self._applied_event_ids.add(event_id)

    def get_due_events(self, simulation_time: float) -> list[TrafficEventBase]:
        """Return scheduled events that are due at simulation_time and not yet applied."""
        due: list[TrafficEventBase] = []
        for e in self._scheduled_events:
            if e.event_id in self._applied_event_ids:
                continue
            if e.starts_at_seconds <= simulation_time + 1e-6:
                due.append(e)
        return due

    def mark_applied(self, event: TrafficEventBase, applied_time: float) -> EventRecord:
        """Mark event as applied and active."""
        self._applied_event_ids.add(event.event_id)
        target = getattr(event, "edge_id", getattr(event, "vehicle_id", "network"))
        rec = EventRecord(
            event_id=event.event_id,
            event_type=event.event_type,
            starts_at_seconds=event.starts_at_seconds,
            duration_seconds=event.duration_seconds,
            applied_at_seconds=applied_time,
            status=EventStatus.ACTIVE,
            target=target,
        )
        self._active_records[event.event_id] = rec
        self._event_history[event.event_id] = rec
        return rec

    def get_expiring_records(self, simulation_time: float) -> list[EventRecord]:
        """Return active event records that have reached their duration expiry at simulation_time."""
        expiring: list[EventRecord] = []
        for rec in self._active_records.values():
            if rec.duration_seconds is not None:
                expiry_time = rec.starts_at_seconds + rec.duration_seconds
                if simulation_time >= expiry_time - 1e-6:
                    expiring.append(rec)
        return expiring

    def mark_resolved(self, event_id: str, resolved_time: float) -> EventRecord | None:
        """Mark active event as resolved."""
        rec = self._active_records.pop(event_id, None)
        if rec is not None:
            resolved_rec = EventRecord(
                event_id=rec.event_id,
                event_type=rec.event_type,
                starts_at_seconds=rec.starts_at_seconds,
                duration_seconds=rec.duration_seconds,
                applied_at_seconds=rec.applied_at_seconds,
                expired_at_seconds=resolved_time,
                status=EventStatus.RESOLVED,
                target=rec.target,
                metadata=rec.metadata,
            )
            self._event_history[event_id] = resolved_rec
            return resolved_rec
        return None

    @property
    def event_history(self) -> tuple[EventRecord, ...]:
        """Return complete event records sorted deterministically by start time and ID."""
        return tuple(
            sorted(
                self._event_history.values(),
                key=lambda r: (r.starts_at_seconds, _event_priority_rank(r.event_type), r.event_id),
            )
        )
