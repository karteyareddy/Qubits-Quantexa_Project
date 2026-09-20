"""Weather domain models and impact definitions."""

from enum import Enum
from pydantic import Field
from app.domain.base import DomainModel, Identifier


class WeatherCondition(str, Enum):
    """Supported meteorological states across urban zones."""

    CLEAR = "clear"
    CLOUDY = "cloudy"
    LIGHT_RAIN = "light_rain"
    HEAVY_RAIN = "heavy_rain"
    FLOODING = "flooding"
    FOG = "fog"
    MIST = "mist"
    STORM = "storm"


class WeatherImpactParameters(DomainModel):
    """Configurable simulation coefficients derived from weather states."""

    road_capacity_factor: float = Field(default=1.0, ge=0.1, le=1.0)
    vehicle_speed_factor: float = Field(default=1.0, ge=0.1, le=1.0)
    lane_availability_ratio: float = Field(default=1.0, ge=0.0, le=1.0)
    visibility_meters: float = Field(default=1000.0, ge=10.0)
    water_level_cm: float = Field(default=0.0, ge=0.0)
    water_flow_speed_mps: float = Field(default=0.0, ge=0.0)
    risk_factor: float = Field(default=0.0, ge=0.0, le=1.0)
    accident_risk_multiplier: float = Field(default=1.0, ge=1.0)


class WeatherZone(DomainModel):
    """A bounded geographic urban zone with its own microclimate."""

    zone_id: Identifier
    name: str
    condition: WeatherCondition = WeatherCondition.CLEAR
    intersection_ids: tuple[Identifier, ...] = ()
    road_ids: tuple[Identifier, ...] = ()
    temperature_c: float = Field(default=22.0)
    rain_intensity_mmh: float = Field(default=0.0, ge=0.0)
    visibility_km: float = Field(default=10.0, ge=0.05)
    water_level_cm: float = Field(default=0.0, ge=0.0)
    water_flow_direction: str = "East"
    impact: WeatherImpactParameters = Field(default_factory=WeatherImpactParameters)


def compute_weather_impact(
    condition: WeatherCondition,
    water_level_cm: float = 0.0,
    rain_intensity_mmh: float = 0.0,
) -> WeatherImpactParameters:
    """Compute explicit simulation parameters for a given weather condition."""
    if condition == WeatherCondition.CLEAR:
        return WeatherImpactParameters(
            road_capacity_factor=1.0,
            vehicle_speed_factor=1.0,
            lane_availability_ratio=1.0,
            visibility_meters=1000.0,
            water_level_cm=0.0,
            water_flow_speed_mps=0.0,
            risk_factor=0.0,
            accident_risk_multiplier=1.0,
        )
    if condition == WeatherCondition.CLOUDY:
        return WeatherImpactParameters(
            road_capacity_factor=0.98,
            vehicle_speed_factor=0.95,
            lane_availability_ratio=1.0,
            visibility_meters=800.0,
            risk_factor=0.05,
        )
    if condition == WeatherCondition.LIGHT_RAIN:
        return WeatherImpactParameters(
            road_capacity_factor=0.85,
            vehicle_speed_factor=0.85,
            lane_availability_ratio=1.0,
            visibility_meters=600.0,
            water_level_cm=max(0.5, water_level_cm),
            risk_factor=0.20,
            accident_risk_multiplier=1.2,
        )
    if condition == WeatherCondition.HEAVY_RAIN:
        return WeatherImpactParameters(
            road_capacity_factor=0.70,
            vehicle_speed_factor=0.75,
            lane_availability_ratio=1.0,
            visibility_meters=350.0,
            water_level_cm=max(3.0, water_level_cm),
            water_flow_speed_mps=0.4,
            risk_factor=0.45,
            accident_risk_multiplier=1.6,
        )
    if condition == WeatherCondition.FLOODING:
        # Water flowing across road; 1 or more lanes unusable
        return WeatherImpactParameters(
            road_capacity_factor=0.40,
            vehicle_speed_factor=0.40,
            lane_availability_ratio=0.50,  # 1 of 2 lanes blocked
            visibility_meters=200.0,
            water_level_cm=max(12.0, water_level_cm),
            water_flow_speed_mps=1.2,
            risk_factor=0.85,
            accident_risk_multiplier=2.5,
        )
    if condition in (WeatherCondition.FOG, WeatherCondition.MIST):
        return WeatherImpactParameters(
            road_capacity_factor=0.65,
            vehicle_speed_factor=0.50,
            lane_availability_ratio=1.0,
            visibility_meters=75.0 if condition == WeatherCondition.FOG else 150.0,
            water_level_cm=0.0,
            water_flow_speed_mps=0.0,
            risk_factor=0.60,
            accident_risk_multiplier=1.8,
        )
    if condition == WeatherCondition.STORM:
        return WeatherImpactParameters(
            road_capacity_factor=0.30,
            vehicle_speed_factor=0.35,
            lane_availability_ratio=0.50,
            visibility_meters=100.0,
            water_level_cm=max(15.0, water_level_cm),
            water_flow_speed_mps=1.8,
            risk_factor=0.95,
            accident_risk_multiplier=3.0,
        )
    return WeatherImpactParameters()
