"""Traffic scenario endpoints."""

from fastapi import APIRouter

from app.api.schemas.network import ScenarioMetadataSchema

scenarios_router = APIRouter(prefix="/scenarios", tags=["Scenarios"])


@scenarios_router.get("", response_model=list[ScenarioMetadataSchema])
def list_scenarios() -> list[ScenarioMetadataSchema]:
    """Expose available deterministic scenario configurations."""
    return [
        ScenarioMetadataSchema(
            scenario_id="normal-traffic",
            name="Scenario 1 — Normal Traffic",
            description="All 4 zones clear (☀️). Baseline free-flow urban traffic across 6 intersections.",
            duration_seconds=300.0,
            vehicle_count=8,
            emergency_vehicle_count=0,
        ),
        ScenarioMetadataSchema(
            scenario_id="heavy-rain",
            name="Scenario 2 — Heavy Rain (Zone 2)",
            description="Zone 2 downpour (🌧️). Road capacity reduced to 70%, vehicle speeds damped to 75%.",
            duration_seconds=300.0,
            vehicle_count=10,
            emergency_vehicle_count=0,
        ),
        ScenarioMetadataSchema(
            scenario_id="flooding",
            name="Scenario 3 — Flooding & Water Flow (Zone 2)",
            description="Zone 2 water flow (🌊). 1 lane blocked, capacity drops to 40%, severe queueing.",
            duration_seconds=300.0,
            vehicle_count=12,
            emergency_vehicle_count=0,
        ),
        ScenarioMetadataSchema(
            scenario_id="fog",
            name="Scenario 4 — Fog / Mist (Zone 3)",
            description="Zone 3 thick mist/fog (🌫️). Visibility drops < 600m, speeds reduced to 50%, longer headway.",
            duration_seconds=300.0,
            vehicle_count=8,
            emergency_vehicle_count=0,
        ),
        ScenarioMetadataSchema(
            scenario_id="mixed-weather",
            name="Scenario 5 — Mixed Weather Multi-Zone",
            description="Zone 1 Clear ☀️, Zone 2 Flood 🌧️🌊, Zone 3 Fog 🌫️, Zone 4 Clear ☀️. Tests global adaptation.",
            duration_seconds=300.0,
            vehicle_count=14,
            emergency_vehicle_count=0,
        ),
        ScenarioMetadataSchema(
            scenario_id="emergency-flood",
            name="Scenario 6 — Emergency Ambulance + Flood",
            description="Active Ambulance traversing while Zone 2 is flooded. System routes around flood + green wave.",
            duration_seconds=300.0,
            vehicle_count=3,
            emergency_vehicle_count=1,
        ),
        ScenarioMetadataSchema(
            scenario_id="emergency-vehicle",
            name="Emergency Priority Scenario",
            description="Normal vehicles plus an active Ambulance requiring green corridor",
            duration_seconds=300.0,
            vehicle_count=3,
            emergency_vehicle_count=1,
        ),
        ScenarioMetadataSchema(
            scenario_id="low-traffic",
            name="Low Traffic Baseline",
            description="3 vehicles routed across the 6-intersection network",
            duration_seconds=300.0,
            vehicle_count=3,
            emergency_vehicle_count=0,
        ),
        ScenarioMetadataSchema(
            scenario_id="congested-traffic",
            name="Congested Traffic Surge",
            description="30 vehicles departing simultaneously causing heavy queueing",
            duration_seconds=300.0,
            vehicle_count=30,
            emergency_vehicle_count=0,
        ),
    ]
