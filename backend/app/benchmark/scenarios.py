"""Scenario definitions for benchmark experiments."""

from app.events.models import (
    AccidentEvent,
    CongestionSpikeEvent,
    EmergencyArrivalEvent,
    RoadClosureEvent,
    TrafficEventBase,
)
from app.simulation.models import SimulationScenario
from app.simulation.scenarios import (
    congested_traffic_scenario,
    emergency_vehicle_scenario,
    low_traffic_scenario,
)


def build_benchmark_scenario(
    scenario_id: str, *, seed: int = 42, duration_seconds: float = 60.0
) -> tuple[SimulationScenario, tuple[TrafficEventBase, ...]]:
    """Build a deterministic simulation scenario and initial scheduled events tuple.

    Returns:
        (SimulationScenario, tuple[TrafficEventBase, ...])
    """
    events: tuple[TrafficEventBase, ...] = ()

    if scenario_id == "low-traffic":
        sc = low_traffic_scenario(seed=seed)
    elif scenario_id == "congested-traffic":
        sc = congested_traffic_scenario(seed=seed)
    elif scenario_id == "dynamic-congestion":
        sc = congested_traffic_scenario(seed=seed)
        events = (
            CongestionSpikeEvent(
                event_id="evt-spike-01",
                starts_at_seconds=15.0,
                edge_id="I1-I2",
                additional_vehicle_count=8,
                duration_seconds=30.0,
            ),
        )
    elif scenario_id == "accident":
        sc = congested_traffic_scenario(seed=seed)
        events = (
            AccidentEvent(
                event_id="evt-accident-01",
                starts_at_seconds=15.0,
                edge_id="I2-I5",
                severity=0.75,
                capacity_factor=0.25,
                duration_seconds=30.0,
            ),
        )
    elif scenario_id == "road-closure":
        sc = low_traffic_scenario(seed=seed)
        events = (
            RoadClosureEvent(
                event_id="evt-closure-01",
                starts_at_seconds=15.0,
                edge_id="I1-I4",
                duration_seconds=30.0,
            ),
        )
    elif scenario_id == "emergency":
        sc = emergency_vehicle_scenario(seed=seed)
        events = (
            EmergencyArrivalEvent(
                event_id="evt-emerg-01",
                starts_at_seconds=10.0,
                vehicle_id="emergency-bmk-001",
                origin="I1",
                destination="I6",
                priority=20,
            ),
        )
    else:
        # Fallback to low-traffic
        sc = low_traffic_scenario(seed=seed)

    # Override duration if requested
    sc = sc.model_copy(update={"duration_seconds": duration_seconds})

    return sc, events
