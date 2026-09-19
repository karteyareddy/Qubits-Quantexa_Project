"""Simulation metrics endpoint."""


from fastapi import APIRouter, Depends

from app.api.dependencies import get_simulation_session
from app.api.schemas.metrics import SimulationMetricsResponse
from app.api.session import SimulationSession

metrics_router = APIRouter(prefix="/simulations", tags=["Metrics"])


@metrics_router.get("/{simulation_id}/metrics", response_model=SimulationMetricsResponse)
def get_simulation_metrics(
    session: SimulationSession = Depends(get_simulation_session),
) -> SimulationMetricsResponse:
    """Retrieve complete metrics snapshot for an active simulation session."""
    return SimulationMetricsResponse.model_validate(session.get_metrics_snapshot())
