"""Tests for events, emergency missions, and metric contracts."""

import pytest
from app.domain.emergency import EmergencyMission, EmergencyMissionStatus
from app.domain.event import EventStatus, EventType, TrafficEvent
from app.domain.metrics import EnvironmentalMetrics
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
    metrics = EnvironmentalMetrics(
        fuel_liters=0.25,
        co2_kg=0.58,
        fuel_liters_per_vehicle=0.25,
        co2_kg_per_vehicle=0.58,
        moving_fuel_liters=0.2,
        idle_fuel_liters=0.05,
    )

    assert metrics.co2_kg == 0.58
    assert metrics.is_estimate is True

    with pytest.raises(ValidationError):
        EnvironmentalMetrics(
            fuel_liters=-1.0,
            co2_kg=0.0,
            fuel_liters_per_vehicle=0.0,
            co2_kg_per_vehicle=0.0,
            moving_fuel_liters=0.0,
            idle_fuel_liters=0.0,
        )
