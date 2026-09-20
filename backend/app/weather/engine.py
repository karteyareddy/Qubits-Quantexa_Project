"""Weather Engine managing urban zones, climate state, and dynamic road impact factors."""

from typing import Any
from app.domain.weather import (
    WeatherCondition,
    WeatherImpactParameters,
    WeatherZone,
    compute_weather_impact,
)


class WeatherEngine:
    """Manages zone-based meteorological states and computes dynamic road impacts."""

    def __init__(self) -> None:
        self._zones: dict[str, WeatherZone] = {}
        self._road_to_zone: dict[str, str] = {}
        self._intersection_to_zone: dict[str, str] = {}
        self._initialize_default_zones()

    def _initialize_default_zones(self) -> None:
        """Create the standard 4-zone layout for the 6-intersection metropolitan network."""
        # Zone 1: Northwest Hub (I1)
        z1 = WeatherZone(
            zone_id="zone-1",
            name="Zone 1 - Northwest Transit Gateway",
            condition=WeatherCondition.CLEAR,
            intersection_ids=("I1",),
            road_ids=("E_I1_I2", "E_I2_I1", "E_I1_I4", "E_I4_I1"),
            temperature_c=24.0,
            visibility_km=10.0,
            impact=compute_weather_impact(WeatherCondition.CLEAR),
        )

        # Zone 2: Central Metro Arterial (I2, I5) - Primary Flood / Heavy Rain Zone
        z2 = WeatherZone(
            zone_id="zone-2",
            name="Zone 2 - Central Grand Corridor",
            condition=WeatherCondition.HEAVY_RAIN,
            intersection_ids=("I2", "I5"),
            road_ids=(
                "E_I1_I2",
                "E_I2_I1",
                "E_I2_I3",
                "E_I3_I2",
                "E_I2_I5",
                "E_I5_I2",
                "E_I4_I5",
                "E_I5_I4",
                "E_I5_I6",
                "E_I6_I5",
            ),
            temperature_c=19.5,
            rain_intensity_mmh=45.0,
            visibility_km=3.5,
            water_level_cm=6.0,
            water_flow_direction="Southeast",
            impact=compute_weather_impact(WeatherCondition.HEAVY_RAIN, water_level_cm=6.0),
        )

        # Zone 3: East Tech District (I3, I6) - Primary Fog / Mist Zone
        z3 = WeatherZone(
            zone_id="zone-3",
            name="Zone 3 - East Innovation District",
            condition=WeatherCondition.FOG,
            intersection_ids=("I3", "I6"),
            road_ids=("E_I2_I3", "E_I3_I2", "E_I3_I6", "E_I6_I3", "E_I5_I6", "E_I6_I5"),
            temperature_c=16.0,
            visibility_km=0.8,
            impact=compute_weather_impact(WeatherCondition.FOG),
        )

        # Zone 4: South Civic & Medical Plaza (I4)
        z4 = WeatherZone(
            zone_id="zone-4",
            name="Zone 4 - South Health & Civic Plaza",
            condition=WeatherCondition.CLEAR,
            intersection_ids=("I4",),
            road_ids=("E_I1_I4", "E_I4_I1", "E_I4_I5", "E_I5_I4"),
            temperature_c=23.0,
            visibility_km=10.0,
            impact=compute_weather_impact(WeatherCondition.CLEAR),
        )

        for z in (z1, z2, z3, z4):
            self._zones[z.zone_id] = z
            for iid in z.intersection_ids:
                self._intersection_to_zone[iid] = z.zone_id
            for rid in z.road_ids:
                self._road_to_zone[rid] = z.zone_id

    def get_all_zones(self) -> list[WeatherZone]:
        """Return all managed weather zones."""
        return list(self._zones.values())

    def get_zone(self, zone_id: str) -> WeatherZone | None:
        """Get a specific zone by ID."""
        return self._zones.get(zone_id)

    def get_zone_for_intersection(self, intersection_id: str) -> WeatherZone | None:
        """Find the weather zone encompassing an intersection."""
        zone_id = self._intersection_to_zone.get(intersection_id)
        return self._zones.get(zone_id) if zone_id else None

    def get_zone_for_road(self, road_id: str) -> WeatherZone | None:
        """Find the weather zone encompassing a road edge."""
        zone_id = self._road_to_zone.get(road_id)
        return self._zones.get(zone_id) if zone_id else None

    def set_zone_condition(
        self,
        zone_id: str,
        condition: WeatherCondition,
        *,
        water_level_cm: float | None = None,
        rain_intensity_mmh: float | None = None,
        visibility_km: float | None = None,
    ) -> WeatherZone:
        """Dynamically update a zone's condition and recompute impact coefficients."""
        zone = self._zones.get(zone_id)
        if not zone:
            raise KeyError(f"Weather zone '{zone_id}' not found")

        w_lvl = water_level_cm if water_level_cm is not None else (
            15.0 if condition == WeatherCondition.FLOODING else (
                5.0 if condition == WeatherCondition.HEAVY_RAIN else 0.0
            )
        )
        r_int = rain_intensity_mmh if rain_intensity_mmh is not None else (
            50.0 if condition in (WeatherCondition.HEAVY_RAIN, WeatherCondition.FLOODING) else (
                10.0 if condition == WeatherCondition.LIGHT_RAIN else 0.0
            )
        )
        vis_km = visibility_km if visibility_km is not None else (
            0.5 if condition == WeatherCondition.FOG else (
                1.5 if condition == WeatherCondition.MIST else 10.0
            )
        )

        impact = compute_weather_impact(condition, water_level_cm=w_lvl, rain_intensity_mmh=r_int)

        updated_zone = zone.model_copy(
            update={
                "condition": condition,
                "water_level_cm": w_lvl,
                "rain_intensity_mmh": r_int,
                "visibility_km": vis_km,
                "impact": impact,
            }
        )
        self._zones[zone_id] = updated_zone
        return updated_zone

    def get_edge_capacity_multiplier(self, road_id: str) -> float:
        """Effective capacity multiplier for road considering weather."""
        zone = self.get_zone_for_road(road_id)
        if not zone:
            return 1.0
        return zone.impact.road_capacity_factor

    def get_edge_speed_multiplier(self, road_id: str) -> float:
        """Effective speed multiplier for road considering weather."""
        zone = self.get_zone_for_road(road_id)
        if not zone:
            return 1.0
        return zone.impact.vehicle_speed_factor

    def is_lane_blocked_by_flood(self, road_id: str) -> bool:
        """True if flooding has blocked one or more lanes."""
        zone = self.get_zone_for_road(road_id)
        if not zone:
            return False
        return zone.condition == WeatherCondition.FLOODING or zone.water_level_cm >= 10.0

    def snapshot_summary(self) -> dict[str, Any]:
        """Serializable telemetry summary for API / WebSocket streaming."""
        return {
            zone_id: {
                "name": z.name,
                "condition": z.condition.value,
                "temperature_c": z.temperature_c,
                "rain_intensity_mmh": z.rain_intensity_mmh,
                "visibility_km": z.visibility_km,
                "water_level_cm": z.water_level_cm,
                "capacity_factor": z.impact.road_capacity_factor,
                "speed_factor": z.impact.vehicle_speed_factor,
                "lane_availability": z.impact.lane_availability_ratio,
                "risk_factor": z.impact.risk_factor,
            }
            for zone_id, z in self._zones.items()
        }


# Global singleton instance
_weather_engine: WeatherEngine | None = None


def get_weather_engine() -> WeatherEngine:
    """Get or instantiate process-level weather engine singleton."""
    global _weather_engine
    if _weather_engine is None:
        _weather_engine = WeatherEngine()
    return _weather_engine
