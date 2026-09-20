"""Canonical deterministic scenarios for the six-intersection demo network."""

from app.domain.network import Network
from app.domain.vehicle import EmergencySubtype
from app.routing.demo_network import build_demo_network
from app.simulation.arrivals import scheduled_arrival
from app.simulation.models import (
    ScheduledArrival,
    SimulationConfiguration,
    SimulationScenario,
)


def low_traffic_scenario(*, seed: int = 42) -> SimulationScenario:
    network = build_demo_network(seed=seed)
    arrivals = (
        scheduled_arrival(
            network,
            vehicle_id="low-001",
            origin="I1",
            destination="I6",
            arrival_time_seconds=0.0,
        ),
        scheduled_arrival(
            network,
            vehicle_id="low-002",
            origin="I4",
            destination="I3",
            arrival_time_seconds=8.0,
        ),
        scheduled_arrival(
            network,
            vehicle_id="low-003",
            origin="I6",
            destination="I1",
            arrival_time_seconds=16.0,
        ),
    )
    return _scenario("low-traffic", seed, network, arrivals)


def congested_traffic_scenario(*, seed: int = 42) -> SimulationScenario:
    network = build_demo_network(seed=seed)
    arrivals = tuple(
        scheduled_arrival(
            network,
            vehicle_id=f"congested-{index + 1:03d}",
            origin="I1",
            destination="I3",
            arrival_time_seconds=0.0,
        )
        for index in range(30)
    )
    return _scenario("congested-traffic", seed, network, arrivals)


def emergency_vehicle_scenario(*, seed: int = 42) -> SimulationScenario:
    network = build_demo_network(seed=seed)
    arrivals = (
        scheduled_arrival(
            network,
            vehicle_id="normal-001",
            origin="I1",
            destination="I6",
            arrival_time_seconds=0.0,
        ),
        scheduled_arrival(
            network,
            vehicle_id="normal-002",
            origin="I4",
            destination="I3",
            arrival_time_seconds=4.0,
        ),
        scheduled_arrival(
            network,
            vehicle_id="emergency-001",
            origin="I1",
            destination="I6",
            arrival_time_seconds=8.0,
            emergency_subtype=EmergencySubtype.AMBULANCE,
            priority_weight=10,
        ),
    )
    return _scenario("emergency-vehicle", seed, network, arrivals)


def normal_traffic_scenario(*, seed: int = 42) -> SimulationScenario:
    """Scenario 1: Normal Traffic - All zones clear with standard vehicle flows."""
    from app.weather.engine import get_weather_engine
    from app.domain.weather import WeatherCondition

    weather = get_weather_engine()
    for zid in ("zone-1", "zone-2", "zone-3", "zone-4"):
        weather.set_zone_condition(zid, WeatherCondition.CLEAR)

    network = build_demo_network(seed=seed)
    arrivals = tuple(
        scheduled_arrival(
            network,
            vehicle_id=f"norm-{idx:03d}",
            origin="I1" if idx % 2 == 0 else "I4",
            destination="I6" if idx % 2 == 0 else "I3",
            arrival_time_seconds=float(idx * 3),
        )
        for idx in range(8)
    )
    return _scenario("normal-traffic", seed, network, arrivals)


def heavy_rain_scenario(*, seed: int = 42) -> SimulationScenario:
    """Scenario 2: Heavy Rain - Zone 2 receives intense downpour and reduced capacity."""
    from app.weather.engine import get_weather_engine
    from app.domain.weather import WeatherCondition

    weather = get_weather_engine()
    weather.set_zone_condition("zone-1", WeatherCondition.CLEAR)
    weather.set_zone_condition("zone-2", WeatherCondition.HEAVY_RAIN, rain_intensity_mmh=45.0)
    weather.set_zone_condition("zone-3", WeatherCondition.CLOUDY)
    weather.set_zone_condition("zone-4", WeatherCondition.CLEAR)

    network = build_demo_network(seed=seed)
    arrivals = tuple(
        scheduled_arrival(
            network,
            vehicle_id=f"rain-{idx:03d}",
            origin="I1" if idx % 2 == 0 else "I4",
            destination="I6" if idx % 2 == 0 else "I3",
            arrival_time_seconds=float(idx * 4),
        )
        for idx in range(10)
    )
    return _scenario("heavy-rain", seed, network, arrivals)


def flooding_scenario(*, seed: int = 42) -> SimulationScenario:
    """Scenario 3: Flooding - Zone 2 water flow across road, 1 lane blocked, queue formation."""
    from app.weather.engine import get_weather_engine
    from app.domain.weather import WeatherCondition

    weather = get_weather_engine()
    weather.set_zone_condition("zone-1", WeatherCondition.CLEAR)
    weather.set_zone_condition("zone-2", WeatherCondition.FLOODING, water_level_cm=14.0)
    weather.set_zone_condition("zone-3", WeatherCondition.LIGHT_RAIN)
    weather.set_zone_condition("zone-4", WeatherCondition.CLEAR)

    network = build_demo_network(seed=seed)
    arrivals = tuple(
        scheduled_arrival(
            network,
            vehicle_id=f"flood-{idx:03d}",
            origin="I1" if idx % 2 == 0 else "I2",
            destination="I6" if idx % 2 == 0 else "I5",
            arrival_time_seconds=float(idx * 3),
        )
        for idx in range(12)
    )
    return _scenario("flooding", seed, network, arrivals)


def fog_scenario(*, seed: int = 42) -> SimulationScenario:
    """Scenario 4: Fog/Mist - Zone 3 low visibility, speed damping, increased headway."""
    from app.weather.engine import get_weather_engine
    from app.domain.weather import WeatherCondition

    weather = get_weather_engine()
    weather.set_zone_condition("zone-1", WeatherCondition.CLEAR)
    weather.set_zone_condition("zone-2", WeatherCondition.CLEAR)
    weather.set_zone_condition("zone-3", WeatherCondition.FOG, visibility_km=0.6)
    weather.set_zone_condition("zone-4", WeatherCondition.CLEAR)

    network = build_demo_network(seed=seed)
    arrivals = tuple(
        scheduled_arrival(
            network,
            vehicle_id=f"fog-{idx:03d}",
            origin="I2" if idx % 2 == 0 else "I5",
            destination="I6" if idx % 2 == 0 else "I3",
            arrival_time_seconds=float(idx * 4),
        )
        for idx in range(8)
    )
    return _scenario("fog", seed, network, arrivals)


def mixed_weather_scenario(*, seed: int = 42) -> SimulationScenario:
    """Scenario 5: Mixed Weather - Zone 1 Clear, Zone 2 Flood, Zone 3 Fog, Zone 4 Clear."""
    from app.weather.engine import get_weather_engine
    from app.domain.weather import WeatherCondition

    weather = get_weather_engine()
    weather.set_zone_condition("zone-1", WeatherCondition.CLEAR)
    weather.set_zone_condition("zone-2", WeatherCondition.FLOODING, water_level_cm=15.0)
    weather.set_zone_condition("zone-3", WeatherCondition.FOG, visibility_km=0.5)
    weather.set_zone_condition("zone-4", WeatherCondition.CLEAR)

    network = build_demo_network(seed=seed)
    arrivals = tuple(
        scheduled_arrival(
            network,
            vehicle_id=f"mixed-{idx:03d}",
            origin="I1" if idx % 2 == 0 else "I4",
            destination="I6" if idx % 2 == 0 else "I3",
            arrival_time_seconds=float(idx * 3),
        )
        for idx in range(14)
    )
    return _scenario("mixed-weather", seed, network, arrivals)


def emergency_flood_scenario(*, seed: int = 42) -> SimulationScenario:
    """Scenario 6: Emergency + Flood - Ambulance transit while central corridor is flooded."""
    from app.weather.engine import get_weather_engine
    from app.domain.weather import WeatherCondition

    weather = get_weather_engine()
    weather.set_zone_condition("zone-1", WeatherCondition.CLEAR)
    weather.set_zone_condition("zone-2", WeatherCondition.FLOODING, water_level_cm=16.0)
    weather.set_zone_condition("zone-3", WeatherCondition.CLOUDY)
    weather.set_zone_condition("zone-4", WeatherCondition.CLEAR)

    network = build_demo_network(seed=seed)
    arrivals = (
        scheduled_arrival(
            network,
            vehicle_id="traffic-001",
            origin="I2",
            destination="I5",
            arrival_time_seconds=0.0,
        ),
        scheduled_arrival(
            network,
            vehicle_id="traffic-002",
            origin="I4",
            destination="I5",
            arrival_time_seconds=3.0,
        ),
        scheduled_arrival(
            network,
            vehicle_id="emergency-amb-01",
            origin="I1",
            destination="I6",
            arrival_time_seconds=6.0,
            emergency_subtype=EmergencySubtype.AMBULANCE,
            priority_weight=15,
        ),
    )
    return _scenario("emergency-flood", seed, network, arrivals)


def _scenario(
    scenario_id: str,
    seed: int,
    network: Network,
    arrivals: tuple[ScheduledArrival, ...],
    duration_seconds: float = 300.0,
) -> SimulationScenario:
    return SimulationScenario(
        scenario_id=scenario_id,
        seed=seed,
        duration_seconds=duration_seconds,
        network=network,
        arrivals=arrivals,
        configuration=SimulationConfiguration(timestep_seconds=1.0),
    )
