"""Traveler Weather Advisory & Route Assistance service."""

from typing import Any
from pydantic import BaseModel, Field
from app.weather.engine import get_weather_engine


class RouteOption(BaseModel):
    """Detailed summary of a candidate traveler path."""

    name: str
    is_recommended: bool
    path_nodes: list[str]
    path_edges: list[str]
    distance_km: float
    eta_minutes: float
    congestion_level: str
    weather_summary: str
    flood_detected: bool
    lanes_available: str
    risk_score: float = Field(ge=0.0, le=1.0)
    warnings: list[str] = Field(default_factory=list)


class TravelerAdvisoryResponse(BaseModel):
    """Traveler advisory report comparing direct vs alternative weather-optimized route."""

    origin: str
    destination: str
    urgency: str
    direct_route: RouteOption
    alternative_route: RouteOption
    recommendation_summary: str
    congestion_avoided_pct: float
    flood_risk_avoided: bool
    travel_time_saved_minutes: float
    advisory_timestamp: float


class TravelerAdvisoryService:
    """Computes weather-aware route evaluations and traveler detour advice."""

    def evaluate_route_advisory(
        self,
        origin: str = "I1",
        destination: str = "I6",
        urgency: str = "normal",
    ) -> TravelerAdvisoryResponse:
        """Analyze direct path vs weather-optimized alternative path."""
        weather = get_weather_engine()
        origin_zone = weather.get_zone_for_intersection(origin)
        dest_zone = weather.get_zone_for_intersection(destination)

        # Standard canonical routes in our 6-intersection arterial grid
        # Direct route goes straight through Central Zone 2 (I1 -> I2 -> I5 -> I6 or I1 -> I2 -> I3 -> I6)
        direct_nodes = ["I1", "I2", "I3", "I6"] if destination in ("I3", "I6") else ["I1", "I2", "I5"]
        direct_edges = ["E_I1_I2", "E_I2_I3", "E_I3_I6"] if destination in ("I3", "I6") else ["E_I1_I2", "E_I2_I5"]

        # Alternative route bypasses Zone 2 central flood by routing via South Gateway (I1 -> I4 -> I5 -> I6)
        alt_nodes = ["I1", "I4", "I5", "I6"] if destination in ("I3", "I6") else ["I1", "I4", "I5"]
        alt_edges = ["E_I1_I4", "E_I4_I5", "E_I5_I6"] if destination in ("I3", "I6") else ["E_I1_I4", "E_I4_I5"]

        # Evaluate Direct Route conditions
        direct_flood = any(weather.is_lane_blocked_by_flood(e) for e in direct_edges)
        direct_speed_mult = min(weather.get_edge_speed_multiplier(e) for e in direct_edges)
        direct_cap_mult = min(weather.get_edge_capacity_multiplier(e) for e in direct_edges)

        direct_dist_km = 4.2
        # Slower speed + capacity drop increases travel time
        direct_eta = round((direct_dist_km / max(15.0, 45.0 * direct_speed_mult)) * 60.0 + (8.0 if direct_flood else 2.0), 1)

        direct_warnings = []
        if direct_flood:
            direct_warnings.append("Water accumulation detected across Grand Pkwy (Zone 2)")
            direct_warnings.append("1 lane blocked due to road water flow (Capacity: 40%)")
            direct_warnings.append("Significant queue backlog and hydroplaning hazard")
        elif direct_speed_mult < 0.8:
            direct_warnings.append("Reduced vehicle speeds due to heavy rain and spray")

        direct_route = RouteOption(
            name="Direct Route (Central Arterial)",
            is_recommended=not direct_flood,
            path_nodes=direct_nodes,
            path_edges=direct_edges,
            distance_km=direct_dist_km,
            eta_minutes=direct_eta,
            congestion_level="High (Gridlock Risk)" if direct_flood else "Moderate",
            weather_summary="Heavy Rain & Water Flow (Zone 2)" if direct_flood else "Rainy",
            flood_detected=direct_flood,
            lanes_available="1 of 2 lanes open" if direct_flood else "2 of 2 lanes open",
            risk_score=0.85 if direct_flood else 0.35,
            warnings=direct_warnings,
        )

        # Evaluate Alternative Route conditions
        alt_dist_km = 4.8  # slightly longer distance but 100% dry and open
        alt_speed_mult = min(weather.get_edge_speed_multiplier(e) for e in alt_edges)
        alt_flood = any(weather.is_lane_blocked_by_flood(e) for e in alt_edges)
        alt_eta = round((alt_dist_km / max(25.0, 50.0 * alt_speed_mult)) * 60.0 + 1.5, 1)

        alt_warnings = []
        if alt_flood:
            alt_warnings.append("Weather alert along southern corridor")
        else:
            alt_warnings.append("Bypasses Zone 2 flood waters via South Civic Corridor")
            alt_warnings.append("Normal road capacity (100%), smooth traffic flow")

        alt_route = RouteOption(
            name="Alternative Route (South Bypass)",
            is_recommended=True if direct_flood else False,
            path_nodes=alt_nodes,
            path_edges=alt_edges,
            distance_km=alt_dist_km,
            eta_minutes=alt_eta,
            congestion_level="Low to Moderate",
            weather_summary="Clear / Light Overcast (Zone 1 & 4)",
            flood_detected=alt_flood,
            lanes_available="2 of 2 lanes open",
            risk_score=0.15,
            warnings=alt_warnings,
        )

        saved_minutes = max(0.0, round(direct_eta - alt_eta, 1))
        congestion_avoided = 58.0 if direct_flood else 15.0

        if direct_flood:
            summary = (
                f"Direct route via {direct_nodes[1]} is heavily impaired by water flow and lane closure. "
                f"Alternative route via {alt_nodes[1]} avoids the flood zone, saving ~{saved_minutes} mins with lower congestion."
            )
        else:
            summary = "Direct route is operating within normal parameters. Weather conditions stable across primary corridors."

        import time

        return TravelerAdvisoryResponse(
            origin=origin,
            destination=destination,
            urgency=urgency,
            direct_route=direct_route,
            alternative_route=alt_route,
            recommendation_summary=summary,
            congestion_avoided_pct=congestion_avoided,
            flood_risk_avoided=direct_flood,
            travel_time_saved_minutes=saved_minutes,
            advisory_timestamp=time.time(),
        )


_advisory_service: TravelerAdvisoryService | None = None


def get_traveler_advisory_service() -> TravelerAdvisoryService:
    """Get singleton advisory service."""
    global _advisory_service
    if _advisory_service is None:
        _advisory_service = TravelerAdvisoryService()
    return _advisory_service
