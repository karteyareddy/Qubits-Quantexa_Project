"""Traffic scenario endpoints."""

from fastapi import APIRouter

from app.api.schemas.network import ScenarioMetadataSchema

scenarios_router = APIRouter(prefix="/scenarios", tags=["Scenarios"])


@scenarios_router.get("", response_model=list[ScenarioMetadataSchema])
def list_scenarios() -> list[ScenarioMetadataSchema]:
    """Expose available deterministic scenario configurations."""
    return [
        ScenarioMetadataSchema(
            scenario_id="low-traffic",
            name="Low Traffic Scenario",
            description="3 vehicles routed across the 6-intersection network",
            duration_seconds=300.0,
            vehicle_count=3,
            emergency_vehicle_count=0,
        ),
        ScenarioMetadataSchema(
            scenario_id="congested-traffic",
            name="Congested Traffic Scenario",
            description="30 vehicles departing simultaneously causing heavy queueing",
            duration_seconds=300.0,
            vehicle_count=30,
            emergency_vehicle_count=0,
        ),
        ScenarioMetadataSchema(
            scenario_id="emergency-vehicle",
            name="Emergency Priority Scenario",
            description="Normal vehicles plus an active Ambulance requiring green corridor",
            duration_seconds=300.0,
            vehicle_count=3,
            emergency_vehicle_count=1,
        ),
    ]
