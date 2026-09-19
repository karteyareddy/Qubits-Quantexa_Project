"""Signal optimization endpoints."""

import time

from fastapi import APIRouter, Depends

from app.api.dependencies import get_simulation_session
from app.api.schemas.optimization import (
    OptimizationRequest,
    OptimizationResponse,
    SignalScheduleItemSchema,
)
from app.api.session import SimulationSession
from app.domain.signal_qubo import SignalSchedule

optimization_router = APIRouter(prefix="/simulations", tags=["Optimization"])


@optimization_router.post(
    "/{simulation_id}/optimize", response_model=OptimizationResponse
)
async def trigger_optimization(
    req: OptimizationRequest,
    session: SimulationSession = Depends(get_simulation_session),
) -> OptimizationResponse:
    """Manually trigger hybrid quantum-classical signal optimization on current simulation state."""
    async with session.lock:
        net_snap, state_snap = session.observer.observe(session.sim)
        current_time = session.sim.state.simulation_time_seconds

        opt_start = time.perf_counter()
        opt_res = session.hybrid_optimizer.optimize(net_snap, state_snap)
        opt_time = time.perf_counter() - opt_start

        applied = False
        schedule_items: list[SignalScheduleItemSchema] = []

        if opt_res.is_feasible and opt_res.selected_schedule is not None:
            sel_sched = opt_res.selected_schedule
            if isinstance(sel_sched, SignalSchedule):
                schedule_map = {
                    d.intersection_id: d.selected_phase.value
                    for d in sel_sched.decisions
                    if d.interval_index == 0
                }
            elif isinstance(sel_sched, dict):
                schedule_map = {
                    k: v.value if hasattr(v, "value") else str(v)
                    for k, v in sel_sched.items()
                }
            else:
                schedule_map = {}

            schedule_items = [
                SignalScheduleItemSchema(
                    intersection_id=intersection_id,
                    selected_phase=phase_id,
                    phase_duration_seconds=30.0,
                )
                for intersection_id, phase_id in schedule_map.items()
            ]

            if req.apply_immediately and isinstance(sel_sched, SignalSchedule):
                session.adaptive_policy.update_schedule(sel_sched, current_time)
                if session.emergency_corridor_enabled:
                    session.emergency_service.update(
                        session.sim,
                        signal_system=session.signal_system,
                        adaptive_policy=session.adaptive_policy,
                    )
                applied = True

        return OptimizationResponse(
            simulation_id=session.simulation_id,
            timestamp=current_time,
            solver_name=opt_res.solver_name,
            qubo_energy=opt_res.selected_energy,
            is_feasible=opt_res.is_feasible,
            selected_schedule=schedule_map if opt_res.is_feasible else None,
            optimization_time_seconds=opt_time,
            fallback_used=opt_res.fallback_used,
            fallback_reason=opt_res.fallback_reason,
            applied_to_simulation=applied,
            schedule_details=schedule_items,
            raw_metrics={
                "status": opt_res.status,
                "mode": opt_res.mode,
                "qaoa_time": opt_res.qaoa_time,
                "classical_time": opt_res.classical_time,
            },
        )
