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
    sim_state = session.sim.state
    scenario_metrics = session.metrics_service.evaluate(
        session.scenario.scenario_id,
        sim_state,
        observations=session.observations,
    )

    tm = scenario_metrics.traffic_metrics
    em = scenario_metrics.environmental_metrics
    egm = scenario_metrics.emergency_metrics

    return SimulationMetricsResponse(
        simulation_id=session.simulation_id,
        simulation_time_seconds=sim_state.simulation_time_seconds,
        total_vehicles=tm.total_vehicles,
        active_vehicles=tm.active_vehicles,
        arrived_vehicles=tm.completed_vehicles,
        completion_rate=tm.completion_rate,
        throughput_vph=tm.throughput_per_minute * 60.0,
        average_travel_time_seconds=tm.average_travel_seconds,
        average_waiting_time_seconds=tm.average_waiting_seconds,
        total_fuel_consumed_liters=em.fuel_liters,
        total_co2_emitted_kg=em.co2_kg,
        emergency_waiting_time_seconds=egm.emergency_average_waiting_seconds,
        emergency_travel_time_seconds=egm.emergency_average_travel_seconds,
        emergency_corridor_active=len(session.emergency_service.active_corridors) > 0,
        event_impact_summary=session.event_engine.get_event_metrics(),
        optimization_summary={
            "total_optimizations": len(session.opt_events),
            "feasible_optimizations": sum(1 for e in session.opt_events if e.is_feasible),
            "total_optimization_time": sum(e.optimization_time for e in session.opt_events),
        },
    )
