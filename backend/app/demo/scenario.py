"""Builder for deterministic hackathon demo scenario and event sequence."""

from app.events.models import (
    CongestionSpikeEvent,
    EmergencyArrivalEvent,
    TrafficEventBase,
)
from app.simulation.models import SimulationScenario
from app.simulation.scenarios import congested_traffic_scenario, low_traffic_scenario


def build_demo_scenario(
    seed: int = 42,
    duration_seconds: float = 60.0,
    demand_level: str = "moderate",
) -> tuple[SimulationScenario, list[TrafficEventBase]]:
    """Construct deterministic 6-intersection network scenario and narrative events."""
    if demand_level == "congested":
        base_scenario = congested_traffic_scenario(seed=seed)
    else:
        base_scenario = low_traffic_scenario(seed=seed)

    # Override duration with demo duration
    config = base_scenario.configuration.model_copy(
        update={"duration_seconds": duration_seconds}
    )
    demo_scenario = SimulationScenario(
        scenario_id="demo-scenario",
        seed=seed,
        duration_seconds=duration_seconds,
        network=base_scenario.network,
        arrivals=base_scenario.arrivals,
        configuration=config,
    )

    # Define pre-scheduled narrative dynamic events
    events: list[TrafficEventBase] = [
        CongestionSpikeEvent(
            event_id="demo-evt-congestion",
            edge_id="I1->I2",
            starts_at_seconds=10.0,
            duration_seconds=25.0,
            additional_vehicle_count=5,
        ),
        EmergencyArrivalEvent(
            event_id="demo-evt-emergency",
            vehicle_id="EMERGENCY_AMBULANCE",
            origin="I1",
            destination="I6",
            starts_at_seconds=20.0,
            priority=10,
        ),
    ]

    return demo_scenario, events
