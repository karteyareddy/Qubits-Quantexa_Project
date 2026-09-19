"""Tests for events, emergency missions, and metric contracts."""

import pytest
from app.domain.emergency import EmergencyMission, EmergencyMissionStatus
from app.domain.event import EventStatus, EventType, TrafficEvent
from app.domain.metrics import EmergencyMetrics, EnvironmentalMetrics, TrafficMetrics
from app.domain.route import Route
from pydantic import ValidationError


@pytest.mark.parametrize("event_type", list(EventType))
def test_all_supported_event_types(event_type: EventType) -> None:
    event = TrafficEvent(
        event_id=f"event-{event_type.value}",
        event_type=event_type,
        starts_at_seconds=60.0,
        duration_seconds=30.0,
        status=EventStatus.ACTIVE,
    )

    assert event.event_type is event_type
    assert event.status is EventStatus.ACTIVE


def test_resolved_event_requires_consistent_timestamp() -> None:
    event = TrafficEvent(
        event_id="event-1",
        event_type=EventType.ACCIDENT,
        starts_at_seconds=10.0,
        status=EventStatus.RESOLVED,
        resolved_at_seconds=20.0,
    )

    assert event.status is EventStatus.RESOLVED

    with pytest.raises(ValidationError, match="resolution timestamp"):
        TrafficEvent(
            event_id="event-2",
            event_type=EventType.CONGESTION,
            starts_at_seconds=10.0,
            status=EventStatus.RESOLVED,
        )


def test_valid_emergency_mission(sample_route: Route) -> None:
    mission = EmergencyMission(
        mission_id="mission-1",
        vehicle_id="ambulance-1",
        origin="I1",
        destination="I2",
        route=sample_route,
        status=EmergencyMissionStatus.ACTIVE,
        requested_at_seconds=20.0,
        started_at_seconds=25.0,
        estimated_arrival_seconds=55.0,
    )

    assert mission.route == sample_route
    assert mission.priority == 10


def test_emergency_mission_rejects_invalid_identity_and_timeline() -> None:
    with pytest.raises(ValidationError):
        EmergencyMission(
            mission_id="",
            vehicle_id="ambulance-1",
            origin="I1",
            destination="I2",
            requested_at_seconds=0.0,
        )

    with pytest.raises(ValidationError, match="cannot precede"):
        EmergencyMission(
            mission_id="mission-1",
            vehicle_id="ambulance-1",
            origin="I1",
            destination="I2",
            requested_at_seconds=20.0,
            started_at_seconds=10.0,
        )


def test_valid_metrics_and_negative_values_rejected() -> None:
    metrics = TrafficMetrics(
        simulation_time_seconds=30.0,
        average_wait_seconds=2.5,
        total_wait_seconds=25.0,
        queue_length=3,
        maximum_queue_length=5,
        throughput=8,
        average_travel_time_seconds=42.0,
        congestion=0.4,
        environmental=EnvironmentalMetrics(
            fuel_liters_estimate=0.25,
            co2_kg_estimate=0.58,
        ),
        emergency=EmergencyMetrics(
            emergency_travel_time_seconds=35.0,
            emergency_completed=True,
        ),
    )

    assert metrics.throughput == 8
    assert metrics.environmental.co2_kg_estimate == 0.58

    with pytest.raises(ValidationError):
        EnvironmentalMetrics(fuel_liters_estimate=-1.0, co2_kg_estimate=0.0)
