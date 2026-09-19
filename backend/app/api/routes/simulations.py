"""Simulation lifecycle and control endpoints."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends

from app.api.dependencies import get_session_manager, get_simulation_session
from app.api.schemas.simulation import (
    SimulationCreateRequest,
    SimulationSessionResponse,
    SimulationStateSnapshot,
    SimulationStepRequest,
)
from app.api.session import SimulationSession, SimulationSessionManager

simulations_router = APIRouter(prefix="/simulations", tags=["Simulations"])


@simulations_router.post("", response_model=SimulationSessionResponse, status_code=201)
def create_simulation(
    req: SimulationCreateRequest,
    mgr: SimulationSessionManager = Depends(get_session_manager),
) -> SimulationSessionResponse:
    """Initialize a new traffic simulation session."""
    sim_id = f"sim-{uuid.uuid4().hex[:8]}"
    session = mgr.create_session(
        simulation_id=sim_id,
        scenario_id=req.scenario_id,
        duration_seconds=req.duration_seconds,
        control_interval_seconds=req.control_interval_seconds,
        seed=req.seed,
        adaptive_enabled=req.adaptive_enabled,
        events_enabled=req.events_enabled,
        emergency_corridor_enabled=req.emergency_corridor_enabled,
    )
    return SimulationSessionResponse(
        simulation_id=session.simulation_id,
        status=session.status,
        scenario_id=session.scenario.scenario_id,
        simulation_time_seconds=session.sim.state.simulation_time_seconds,
        created_at=session.created_at,
    )


@simulations_router.get("/{simulation_id}", response_model=SimulationStateSnapshot)
def get_simulation_state(
    session: SimulationSession = Depends(get_simulation_session),
) -> dict[str, Any]:
    """Retrieve full simulation state snapshot."""
    return session.get_state_snapshot()


@simulations_router.post("/{simulation_id}/start", response_model=SimulationSessionResponse)
def start_simulation(
    session: SimulationSession = Depends(get_simulation_session),
) -> SimulationSessionResponse:
    """Start simulation runner execution state."""
    session.status = "running"
    return SimulationSessionResponse(
        simulation_id=session.simulation_id,
        status=session.status,
        scenario_id=session.scenario.scenario_id,
        simulation_time_seconds=session.sim.state.simulation_time_seconds,
        created_at=session.created_at,
    )


@simulations_router.post("/{simulation_id}/pause", response_model=SimulationSessionResponse)
def pause_simulation(
    session: SimulationSession = Depends(get_simulation_session),
) -> SimulationSessionResponse:
    """Pause simulation runner execution state."""
    if session.status != "completed":
        session.status = "paused"
    return SimulationSessionResponse(
        simulation_id=session.simulation_id,
        status=session.status,
        scenario_id=session.scenario.scenario_id,
        simulation_time_seconds=session.sim.state.simulation_time_seconds,
        created_at=session.created_at,
    )


@simulations_router.post("/{simulation_id}/step", response_model=SimulationStateSnapshot)
async def step_simulation(
    req: SimulationStepRequest,
    session: SimulationSession = Depends(get_simulation_session),
) -> dict[str, Any]:
    """Advance simulation state by specified step duration."""
    return await session.step(step_seconds=req.step_seconds)


@simulations_router.post("/{simulation_id}/stop", response_model=SimulationSessionResponse)
def stop_simulation(
    session: SimulationSession = Depends(get_simulation_session),
    mgr: SimulationSessionManager = Depends(get_session_manager),
) -> SimulationSessionResponse:
    """Stop and release simulation session."""
    session.status = "completed"
    resp = SimulationSessionResponse(
        simulation_id=session.simulation_id,
        status=session.status,
        scenario_id=session.scenario.scenario_id,
        simulation_time_seconds=session.sim.state.simulation_time_seconds,
        created_at=session.created_at,
    )
    return resp
