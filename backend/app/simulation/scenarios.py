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


def _scenario(
    scenario_id: str,
    seed: int,
    network: Network,
    arrivals: tuple[ScheduledArrival, ...],
) -> SimulationScenario:
    return SimulationScenario(
        scenario_id=scenario_id,
        seed=seed,
        duration_seconds=120.0,
        network=network,
        arrivals=arrivals,
        configuration=SimulationConfiguration(timestep_seconds=1.0),
    )
