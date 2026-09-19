"""Transparent prototype fuel and CO2 estimates."""

from collections.abc import Sequence

from pydantic import Field

from app.domain.base import DomainModel
from app.domain.metrics import EnvironmentalMetrics
from app.domain.vehicle import Vehicle


class EnvironmentalConfig(DomainModel):
    """Configurable prototype assumptions, not calibrated measurements."""

    moving_fuel_l_per_hour: float = Field(default=2.4, ge=0.0)
    idle_fuel_l_per_hour: float = Field(default=0.08, ge=0.0)
    co2_kg_per_liter: float = Field(default=2.31, ge=0.0)


def estimate_environmental_metrics(
    vehicles: Sequence[Vehicle],
    *,
    config: EnvironmentalConfig | None = None,
) -> EnvironmentalMetrics:
    """Estimate fuel from moving/waiting time without double counting."""
    assumptions = config or EnvironmentalConfig()
    moving_seconds = sum(
        max(vehicle.total_travel_time_seconds - vehicle.waiting_time_seconds, 0.0)
        for vehicle in vehicles
    )
    waiting_seconds = sum(vehicle.waiting_time_seconds for vehicle in vehicles)
    moving_fuel = moving_seconds / 3600.0 * assumptions.moving_fuel_l_per_hour
    idle_fuel = waiting_seconds / 3600.0 * assumptions.idle_fuel_l_per_hour
    fuel = moving_fuel + idle_fuel
    co2 = fuel * assumptions.co2_kg_per_liter
    vehicle_count = len(vehicles)
    return EnvironmentalMetrics(
        fuel_liters=fuel,
        co2_kg=co2,
        fuel_liters_per_vehicle=fuel / vehicle_count if vehicle_count else 0.0,
        co2_kg_per_vehicle=co2 / vehicle_count if vehicle_count else 0.0,
        moving_fuel_liters=moving_fuel,
        idle_fuel_liters=idle_fuel,
    )
