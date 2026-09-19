"""Dynamic traffic event execution engine."""

from typing import Any

from app.events.handlers import EventHandlerError, apply_event, restore_event_effect
from app.events.models import EventRecord, EventStatus
from app.events.scheduler import EventScheduler
from app.simulation.engine import TrafficSimulation


class EventEngine:
    """Manages deterministic scheduling, execution, and lifecycle of traffic events."""

    def __init__(
        self,
        scheduler: EventScheduler | None = None,
        *,
        fail_fast: bool = True,
    ) -> None:
        self._scheduler = scheduler or EventScheduler()
        self._fail_fast = fail_fast
        self._active_effects: dict[str, dict[str, Any]] = {}
        self._history: dict[str, EventRecord] = {}

    @property
    def scheduler(self) -> EventScheduler:
        return self._scheduler

    @property
    def history(self) -> tuple[EventRecord, ...]:
        return tuple(self._history.values())

    @property
    def active_records(self) -> tuple[EventRecord, ...]:
        return tuple(
            rec for rec in self._history.values() if rec.status == EventStatus.ACTIVE
        )

    def process_due_events(self, simulation: TrafficSimulation) -> list[EventRecord]:
        """Apply events scheduled at or before the current simulation time."""
        current_time = simulation.state.simulation_time_seconds
        due_events = self._scheduler.get_due_events(current_time)
        applied_records: list[EventRecord] = []

        for event in due_events:
            record = apply_event(event, simulation, self._active_effects)
            self._history[event.event_id] = record
            self._scheduler.mark_processed(event.event_id)
            applied_records.append(record)

            if record.status == EventStatus.FAILED and self._fail_fast:
                raise EventHandlerError(
                    f"Event {event.event_id} failed: {record.failure_reason}"
                )

        self._check_expirations(simulation, current_time)
        return applied_records

    def check_expirations(self, simulation: TrafficSimulation) -> list[EventRecord]:
        """Check and restore expired events at current simulation time."""
        current_time = simulation.state.simulation_time_seconds
        return self._check_expirations(simulation, current_time)

    def _check_expirations(
        self, simulation: TrafficSimulation, current_time: float
    ) -> list[EventRecord]:
        expired_records: list[EventRecord] = []
        for event_id, record in list(self._history.items()):
            if (
                record.status == EventStatus.ACTIVE
                and record.expired_time is not None
                and current_time >= record.expired_time
            ):
                restore_event_effect(event_id, simulation, self._active_effects)
                updated_record = record.model_copy(
                    update={"status": EventStatus.EXPIRED}
                )
                self._history[event_id] = updated_record
                expired_records.append(updated_record)
        return expired_records

    def get_event_metrics(self) -> dict[str, Any]:
        """Aggregate event statistics for diagnostic logging and metrics."""
        events_by_type: dict[str, int] = {}
        for rec in self._history.values():
            events_by_type[rec.event_type] = events_by_type.get(rec.event_type, 0) + 1

        return {
            "total_events": len(self._history),
            "active_event_count": len(self.active_records),
            "completed_events": sum(
                1
                for r in self._history.values()
                if r.status in (EventStatus.EXPIRED, EventStatus.RESOLVED)
            ),
            "failed_events": sum(
                1 for r in self._history.values() if r.status == EventStatus.FAILED
            ),
            "events_by_type": events_by_type,
        }
