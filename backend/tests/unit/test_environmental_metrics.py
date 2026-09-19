"""Unit tests for transparent prototype fuel and CO2 estimates."""

import pytest
from app.domain.vehicle import Vehicle, VehicleType
from app.metrics.environmental import EnvironmentalConfig, estimate_environmental_metrics


def test_moving_idle_combined_and_per_vehicle_estimates() -> None:
    moving = _vehicle("moving", total_travel=3600.0, waiting=0.0)
    idle = _vehicle("idle", total_travel=3600.0, waiting=3600.0)
    config = EnvironmentalConfig(
        moving_fuel_l_per_hour=2.4,
        idle_fuel_l_per_hour=0.08,
        co2_kg_per_liter=2.31,
    )

    metrics = estimate_environmental_metrics((moving, idle), config=config)

    assert metrics.moving_fuel_liters == pytest.approx(2.4)
    assert metrics.idle_fuel_liters == pytest.approx(0.08)
    assert metrics.fuel_liters == pytest.approx(2.48)
    assert metrics.co2_kg == pytest.approx(2.48 * 2.31)
    assert metrics.fuel_liters_per_vehicle == pytest.approx(1.24)
    assert metrics.co2_kg_per_vehicle == pytest.approx(2.48 * 2.31 / 2)


def test_waiting_time_is_not_double_counted_as_moving_time() -> None:
    vehicle = _vehicle("waiting", total_travel=10.0, waiting=15.0)

    metrics = estimate_environmental_metrics((vehicle,))

    assert metrics.moving_fuel_liters == 0.0
    assert metrics.idle_fuel_liters > 0.0


def _vehicle(vehicle_id: str, *, total_travel: float, waiting: float) -> Vehicle:
    return Vehicle(
        vehicle_id=vehicle_id,
        vehicle_type=VehicleType.REGULAR,
        origin="I1",
        destination="I2",
        total_travel_time_seconds=total_travel,
        waiting_time_seconds=waiting,
        stopped_time_seconds=waiting,
    )
