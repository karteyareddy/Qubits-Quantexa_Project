"""Unit tests for the Weather Engine and Traveler Advisory systems."""

import pytest
from app.domain.weather import WeatherCondition, compute_weather_impact
from app.weather.engine import WeatherEngine
from app.routing.traveler_advisory import TravelerAdvisoryService


def test_compute_weather_impact_clear_vs_flooding() -> None:
    clear_impact = compute_weather_impact(WeatherCondition.CLEAR)
    assert clear_impact.road_capacity_factor == 1.0
    assert clear_impact.vehicle_speed_factor == 1.0
    assert clear_impact.water_level_cm == 0.0

    flood_impact = compute_weather_impact(WeatherCondition.FLOODING, water_level_cm=15.0)
    assert flood_impact.road_capacity_factor == 0.40
    assert flood_impact.vehicle_speed_factor == 0.40
    assert flood_impact.lane_availability_ratio == 0.50
    assert flood_impact.risk_factor > 0.7


def test_weather_engine_zones_and_impact() -> None:
    engine = WeatherEngine()
    zones = engine.get_all_zones()
    assert len(zones) == 4

    zone2 = engine.get_zone("zone-2")
    assert zone2 is not None
    assert "I2" in zone2.intersection_ids

    # Update Zone 2 to Flooding
    updated = engine.set_zone_condition("zone-2", WeatherCondition.FLOODING, water_level_cm=18.0)
    assert updated.condition == WeatherCondition.FLOODING
    assert engine.is_lane_blocked_by_flood("E_I1_I2") is True
    assert engine.get_edge_capacity_multiplier("E_I1_I2") == 0.40
    assert engine.get_edge_speed_multiplier("E_I1_I2") == 0.40


def test_traveler_advisory_flood_warning() -> None:
    from app.weather.engine import get_weather_engine

    engine = get_weather_engine()
    engine.set_zone_condition("zone-2", WeatherCondition.FLOODING, water_level_cm=14.0)

    service = TravelerAdvisoryService()
    advisory = service.evaluate_route_advisory(origin="I1", destination="I6")

    assert advisory.direct_route.flood_detected is True
    assert advisory.direct_route.is_recommended is False
    assert any("Water accumulation" in w for w in advisory.direct_route.warnings)

    assert advisory.alternative_route.is_recommended is True
    assert advisory.alternative_route.flood_detected is False
    assert advisory.flood_risk_avoided is True
