"""Weather and Traveler Advisory API endpoints."""

from typing import Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from app.domain.weather import WeatherCondition
from app.routing.traveler_advisory import (
    TravelerAdvisoryResponse,
    get_traveler_advisory_service,
)
from app.weather.engine import get_weather_engine

weather_router = APIRouter(tags=["Weather & Traveler Advisory"])


class UpdateZoneWeatherRequest(BaseModel):
    """Payload to modify a zone's meteorological condition."""

    condition: WeatherCondition
    water_level_cm: float | None = Field(default=None, ge=0.0)
    rain_intensity_mmh: float | None = Field(default=None, ge=0.0)
    visibility_km: float | None = Field(default=None, ge=0.05)


class TravelerAdvisoryRequest(BaseModel):
    """Payload to request route advisory between intersections."""

    origin: str = Field(default="I1", description="Origin intersection ID")
    destination: str = Field(default="I6", description="Destination intersection ID")
    urgency: str = Field(default="normal", description="normal | high | emergency")


@weather_router.get("/weather/zones")
def get_weather_zones() -> dict[str, Any]:
    """Retrieve current microclimate and impact coefficients across all zones."""
    weather = get_weather_engine()
    return {
        "zones": [z.model_dump() for z in weather.get_all_zones()],
        "summary": weather.snapshot_summary(),
    }


@weather_router.post("/weather/zones/{zone_id}")
def update_weather_zone(zone_id: str, request: UpdateZoneWeatherRequest) -> dict[str, Any]:
    """Dynamically set the weather state for an urban zone (Clear, Heavy Rain, Flood, Fog)."""
    weather = get_weather_engine()
    try:
        updated = weather.set_zone_condition(
            zone_id,
            request.condition,
            water_level_cm=request.water_level_cm,
            rain_intensity_mmh=request.rain_intensity_mmh,
            visibility_km=request.visibility_km,
        )
        return {
            "status": "success",
            "message": f"Updated {zone_id} to {request.condition.value}",
            "zone": updated.model_dump(),
        }
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@weather_router.post("/routes/traveler-advisory", response_model=TravelerAdvisoryResponse)
def get_traveler_route_advisory(request: TravelerAdvisoryRequest) -> TravelerAdvisoryResponse:
    """Generate weather-aware traveler route recommendations and flood hazard warnings."""
    service = get_traveler_advisory_service()
    return service.evaluate_route_advisory(
        origin=request.origin,
        destination=request.destination,
        urgency=request.urgency,
    )
