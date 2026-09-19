"""Unit tests for event models and scheduler."""

import pytest
from app.events.models import (
    AccidentEvent,
    CongestionSpikeEvent,
    EmergencyArrivalEvent,
    EventType,
    RoadClosureEvent,
)
from app.events.scheduler import EventScheduler
from pydantic import ValidationError


def test_event_models_validation() -> None:
    # Congestion spike
    cs = CongestionSpikeEvent(
        event_id="cs1",
        timestamp=10.0,
        target="I1->I2",
        additional_vehicle_count=5,
    )
    assert cs.event_type == EventType.CONGESTION.value
    assert cs.additional_vehicle_count == 5

    with pytest.raises(ValidationError):
        CongestionSpikeEvent(
            event_id="cs_bad",
            timestamp=-1.0,
            target="I1->I2",
            additional_vehicle_count=0,
        )

    # Accident
    acc = AccidentEvent(
        event_id="acc1",
        timestamp=15.0,
        target="I2->I5",
        severity=0.8,
        capacity_factor=0.25,
        duration=30.0,
    )
    assert acc.event_type == EventType.ACCIDENT.value
    assert acc.capacity_factor == 0.25

    with pytest.raises(ValidationError):
        AccidentEvent(
            event_id="acc_bad",
            timestamp=5.0,
            target="I2->I5",
            capacity_factor=1.5,
        )

    # Road closure
    rc = RoadClosureEvent(
        event_id="rc1",
        timestamp=20.0,
        target="I1->I4",
        duration=50.0,
    )
    assert rc.event_type == EventType.ROAD_CLOSURE.value

    # Emergency arrival
    em = EmergencyArrivalEvent(
        event_id="em1",
        timestamp=25.0,
        target="I1",
        vehicle_id="amb_01",
        origin="I1",
        destination="I6",
        priority=10,
    )
    assert em.event_type == EventType.EMERGENCY_ARRIVAL.value
    assert em.priority == 10


def test_event_scheduler_ordering_and_due_filtering() -> None:
    scheduler = EventScheduler()

    e1 = CongestionSpikeEvent(event_id="cs1", timestamp=20.0, target="I1->I2", additional_vehicle_count=2)
    e2 = AccidentEvent(event_id="acc1", timestamp=20.0, target="I2->I5", capacity_factor=0.5)
    e3 = RoadClosureEvent(event_id="rc1", timestamp=20.0, target="I1->I4", duration=10.0)
    e4 = EmergencyArrivalEvent(event_id="em1", timestamp=20.0, target="I1", vehicle_id="amb1", origin="I1", destination="I6")
    e5 = RoadClosureEvent(event_id="rc0", timestamp=10.0, target="I2->I3", duration=5.0)

    scheduler.add_events([e1, e2, e3, e4, e5])

    due_at_15 = scheduler.get_due_events(15.0)
    assert len(due_at_15) == 1
    assert due_at_15[0].event_id == "rc0"

    due_at_20 = scheduler.get_due_events(20.0)
    # Total due should be 5 events (including rc0 if not marked processed)
    assert len(due_at_20) == 5

    # Check tie-breaker ordering at timestamp 20.0:
    # Priority rank: ROAD_CLOSURE (10) < ACCIDENT (20) < CONGESTION_SPIKE (30) < EMERGENCY_ARRIVAL (40)
    events_at_20 = [e for e in due_at_20 if e.timestamp == 20.0]
    assert [e.event_id for e in events_at_20] == ["rc1", "acc1", "cs1", "em1"]


def test_event_scheduler_idempotency() -> None:
    scheduler = EventScheduler()
    e1 = CongestionSpikeEvent(event_id="cs1", timestamp=10.0, target="I1->I2", additional_vehicle_count=1)
    scheduler.add_event(e1)

    with pytest.raises(ValueError, match="Duplicate event_id"):
        scheduler.add_event(e1)

    assert not scheduler.is_processed("cs1")
    scheduler.mark_processed("cs1")
    assert scheduler.is_processed("cs1")

    # Due events should exclude processed events
    due = scheduler.get_due_events(10.0)
    assert len(due) == 0
