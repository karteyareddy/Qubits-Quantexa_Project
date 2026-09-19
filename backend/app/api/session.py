"""Simulation Session Manager handling lifecycle, state snapshot, and async execution loop."""

import asyncio
import logging
import time
from typing import Any

from app.adaptive.config import AdaptiveConfig
from app.adaptive.controller import AdaptiveSignalPolicy
from app.adaptive.models import AdaptiveOptimizationEvent
from app.adaptive.observer import TrafficObserver
from app.adaptive.scheduler import AdaptiveScheduler
from app.api.errors import APIException
from app.emergency.service import EmergencyCorridorService
from app.events.engine import EventEngine
from app.hardening.determinism import seed_all
from app.hardening.limits import DEFAULT_PLATFORM_LIMITS
from app.metrics.service import MetricsService
from app.optimization.hybrid_solver import HybridSignalOptimizer
from app.signals.policy import SignalSystem
from app.simulation.engine import TrafficSimulation
from app.simulation.models import SimulationScenario, SimulationState
from app.simulation.scenarios import (
    congested_traffic_scenario,
    emergency_vehicle_scenario,
    low_traffic_scenario,
)

logger = logging.getLogger(__name__)


def get_scenario_by_id(scenario_id: str, seed: int = 42) -> SimulationScenario:
    """Retrieve canonical scenario by ID."""
    scenarios: dict[str, Any] = {
        "low-traffic": low_traffic_scenario(seed=seed),
        "congested-traffic": congested_traffic_scenario(seed=seed),
        "emergency-vehicle": emergency_vehicle_scenario(seed=seed),
    }
    if scenario_id not in scenarios:
        raise APIException(
            status_code=404,
            code="SCENARIO_NOT_FOUND",
            message=f"Scenario '{scenario_id}' not found. Available: {list(scenarios.keys())}",
        )
    return scenarios[scenario_id]  # type: ignore[no-any-return]


class SimulationSession:
    """Individual active simulation session maintaining engine components and async lock."""

    def __init__(
        self,
        simulation_id: str,
        scenario: SimulationScenario,
        duration_seconds: float | None = None,
        control_interval_seconds: float = 5.0,
        seed: int = 42,
        adaptive_enabled: bool = True,
        events_enabled: bool = True,
        emergency_corridor_enabled: bool = True,
    ) -> None:
        self.simulation_id = simulation_id
        raw_duration = duration_seconds if duration_seconds is not None else scenario.duration_seconds
        self.requested_duration = DEFAULT_PLATFORM_LIMITS.validate_simulation_duration(raw_duration)
        self.scenario = scenario.model_copy(
            update={"duration_seconds": self.requested_duration}
        )
        self.status = "created"  # created, running, paused, completed, failed
        self.created_at = time.time()
        self.seed = seed
        self.adaptive_enabled = adaptive_enabled
        self.events_enabled = events_enabled
        self.emergency_corridor_enabled = emergency_corridor_enabled

        # Set seed for determinism
        seed_all(seed)

        # Initialize domain & engine services
        self.adaptive_config = AdaptiveConfig(
            control_interval_seconds=control_interval_seconds,
        )
        self.signal_system = SignalSystem.for_network(self.scenario.network)
        self.adaptive_policy = AdaptiveSignalPolicy(
            signal_system=self.signal_system,
            network=self.scenario.network,
        )
        self.sim = TrafficSimulation(self.scenario, entry_policy=self.adaptive_policy)

        self.observer = TrafficObserver()
        self.scheduler = AdaptiveScheduler(config=self.adaptive_config)
        self.hybrid_optimizer = HybridSignalOptimizer(config=self.adaptive_config.hybrid_config)
        self.event_engine = EventEngine()
        self.emergency_service = EmergencyCorridorService()
        self.metrics_service = MetricsService()

        self.observations: list[SimulationState] = []
        self.opt_events: list[AdaptiveOptimizationEvent] = []
        self.interval_idx = 0

        self.lock = asyncio.Lock()
        self._runner_task: asyncio.Task[None] | None = None

    def extend_duration(self, minimum_duration_seconds: float) -> None:
        """Extend both session and engine horizons for newly scheduled traffic."""
        if minimum_duration_seconds <= self.requested_duration:
            return
        validated_duration = DEFAULT_PLATFORM_LIMITS.validate_simulation_duration(
            minimum_duration_seconds
        )
        self.requested_duration = validated_duration
        self.scenario = self.scenario.model_copy(
            update={"duration_seconds": validated_duration}
        )
        self.sim.extend_duration(validated_duration)

    async def step(self, step_seconds: float = 1.0) -> dict[str, Any]:
        """Advance simulation by step_seconds under session lock."""
        async with self.lock:
            return self._step_sync(step_seconds)

    def _step_sync(self, step_seconds: float = 1.0) -> dict[str, Any]:
        """Synchronous step logic inside session lock."""
        if self.status == "completed":
            return self.get_state_snapshot()

        steps_to_take = max(1, round(step_seconds / self.sim.scenario.configuration.timestep_seconds))

        for _ in range(steps_to_take):
            if self.sim.state.simulation_time_seconds >= self.requested_duration:
                self.status = "completed"
                break

            current_time = self.sim.state.simulation_time_seconds

            # 1. Process due dynamic events
            if self.events_enabled:
                self.event_engine.process_due_events(self.sim)

            # 2. Update emergency corridors & preemption
            if self.emergency_corridor_enabled:
                self.emergency_service.update(
                    self.sim,
                    signal_system=self.signal_system,
                    adaptive_policy=self.adaptive_policy,
                )

            # 3. Record observation
            self.observations.append(self.sim.state)

            # 4. Check adaptive optimization schedule
            if self.adaptive_enabled and self.scheduler.is_optimization_due(current_time):
                net_snap, state_snap = self.observer.observe(self.sim)
                opt_start = time.perf_counter()
                opt_res = self.hybrid_optimizer.optimize(net_snap, state_snap)
                opt_time = time.perf_counter() - opt_start

                status_str = opt_res.status
                schedule = None

                if opt_res.is_feasible and opt_res.selected_schedule is not None:
                    schedule = opt_res.selected_schedule
                    self.adaptive_policy.update_schedule(schedule, current_time)
                    if self.emergency_corridor_enabled:
                        self.emergency_service.update(
                            self.sim,
                            signal_system=self.signal_system,
                            adaptive_policy=self.adaptive_policy,
                        )
                else:
                    status_str = "retained_previous"

                self.opt_events.append(
                    AdaptiveOptimizationEvent(
                        timestamp=current_time,
                        interval_index=self.interval_idx,
                        status=status_str,
                        solver_name=opt_res.solver_name,
                        qubo_energy=opt_res.selected_energy,
                        is_feasible=opt_res.is_feasible,
                        schedule=schedule,
                        optimization_time=opt_time,
                        fallback_used=opt_res.fallback_used,
                        fallback_reason=opt_res.fallback_reason,
                    )
                )
                self.scheduler.mark_optimized(current_time)
                self.interval_idx += 1

            # 5. Advance simulation step
            self.sim.step()

            # 6. Check expirations & emergency updates after step
            if self.events_enabled:
                self.event_engine.check_expirations(self.sim)
            if self.emergency_corridor_enabled:
                self.emergency_service.update(
                    self.sim,
                    signal_system=self.signal_system,
                    adaptive_policy=self.adaptive_policy,
                )

        return self.get_state_snapshot()

    def get_state_snapshot(self) -> dict[str, Any]:
        """Build serializable state snapshot for REST and WebSockets."""
        sim_state = self.sim.state

        all_vehicles = list(sim_state.pending_vehicles) + list(sim_state.active_vehicles) + list(sim_state.completed_vehicles)
        vehicles_data = [
            {
                "vehicle_id": v.vehicle_id,
                "origin": v.origin,
                "destination": v.destination,
                "current_edge_id": v.current_edge_id,
                "route": list(v.route.edge_ids) if v.route is not None else [],
                "route_index": v.current_route_index,
                "arrival_time_seconds": v.arrival_time_seconds,
                "distance_on_current_edge_meters": v.position_on_edge * 500.0,
                "accumulated_waiting_time_seconds": v.waiting_time_seconds,
                "speed_mps": v.speed_kph / 3.6,
                "is_emergency": v.is_emergency,
                "emergency_subtype": (
                    v.emergency_subtype.value if v.emergency_subtype is not None else None
                ),
                "priority_weight": v.priority_weight,
                "has_arrived": v.state.value == "arrived",
                "departure_time_seconds": v.arrival_time_seconds,
            }
            for v in all_vehicles
        ]

        signal_states = self.adaptive_policy.states_at(sim_state.simulation_time_seconds)
        signals_data = [
            {
                "intersection_id": s.intersection_id,
                "current_phase": s.current_phase.value,
                "time_in_phase_seconds": s.phase_elapsed_seconds,
                "active_green_approaches": [
                    app_st.approach_id
                    for app_st in s.approach_states
                    if app_st.indication.value == "GREEN"
                ],
            }
            for s in signal_states
        ]

        active_events_data = [
            {
                "event_id": ev.event_id,
                "event_type": ev.event_type.value,
                "timestamp": ev.starts_at_seconds,
                "duration": ev.duration_seconds or 0.0,
                "status": ev.status.value,
                "target": ev.target,
            }
            for ev in self.event_engine.active_records
        ]

        closed_targets = {ev.target for ev in self.event_engine.active_records if ev.event_type.value == "road_closure"}

        edges_data = [
            {
                "edge_id": e.edge_id,
                "vehicle_ids": list(sim_state.edge_occupancy.get(e.edge_id, ())),
                "vehicle_count": len(sim_state.edge_occupancy.get(e.edge_id, ())),
                "capacity": e.capacity,
                "effective_capacity": e.capacity,
                "travel_time_multiplier": 1.0 + e.congestion / 20.0,
                "is_closed": e.edge_id in closed_targets or e.capacity == 0.0,
            }
            for e in self.scenario.network.edges
        ]

        active_corridors_data = [
            {
                "corridor_id": c.corridor_id,
                "vehicle_id": c.vehicle_id,
                "route": list(c.route.edge_ids) if hasattr(c.route, "edge_ids") else list(c.route),
                "intersections": [reservation.intersection_id for reservation in c.intersections],
                "status": c.status.value,
                "created_at_seconds": c.created_at_seconds,
                "activated_at_seconds": c.activated_at_seconds,
                "released_at_seconds": c.released_at_seconds,
                "green_windows": [
                    {
                        "intersection_id": reservation.intersection_id,
                        "arrival_time_seconds": reservation.arrival_time_seconds,
                        "window_start_seconds": reservation.green_window_start,
                        "window_end_seconds": reservation.green_window_end,
                        "incoming_approach": reservation.incoming_edge_id,
                        "outgoing_approach": reservation.outgoing_edge_id,
                        "required_phase": reservation.required_phase.value,
                    }
                    for reservation in c.intersections
                ],
                "failure_reason": c.failure_reason,
            }
            for c in self.emergency_service.corridor_history
        ]

        return {
            "simulation_id": self.simulation_id,
            "status": self.status,
            "simulation_time_seconds": sim_state.simulation_time_seconds,
            "vehicles": vehicles_data,
            "signals": signals_data,
            "edges": edges_data,
            "active_events": active_events_data,
            "emergency_corridors": active_corridors_data,
            "metrics": self.get_metrics_snapshot(),
            "latest_optimization": self.get_latest_optimization_snapshot(),
        }

    def get_metrics_snapshot(self) -> dict[str, Any]:
        """Build the flat metrics contract shared by REST and live snapshots."""
        sim_state = self.sim.state
        current_metrics = self.metrics_service.evaluate(
            self.scenario.scenario_id,
            sim_state,
            observations=self.observations,
        )
        traffic = current_metrics.traffic_metrics
        environmental = current_metrics.environmental_metrics
        emergency = current_metrics.emergency_metrics

        return {
            "simulation_id": self.simulation_id,
            "simulation_time_seconds": sim_state.simulation_time_seconds,
            "total_vehicles": traffic.total_vehicles,
            "active_vehicles": traffic.active_vehicles,
            "arrived_vehicles": traffic.completed_vehicles,
            "completion_rate": traffic.completion_rate,
            "throughput_vph": traffic.throughput_per_minute * 60.0,
            "average_travel_time_seconds": traffic.average_travel_seconds,
            "average_waiting_time_seconds": traffic.average_waiting_seconds,
            "total_fuel_consumed_liters": environmental.fuel_liters,
            "total_co2_emitted_kg": environmental.co2_kg,
            "emergency_waiting_time_seconds": emergency.emergency_average_waiting_seconds,
            "emergency_travel_time_seconds": emergency.emergency_average_travel_seconds,
            "emergency_corridor_active": bool(self.emergency_service.active_corridors),
            "event_impact_summary": self.event_engine.get_event_metrics(),
            "optimization_summary": {
                "total_optimizations": len(self.opt_events),
                "feasible_optimizations": sum(1 for event in self.opt_events if event.is_feasible),
                "total_optimization_time": sum(
                    event.optimization_time for event in self.opt_events
                ),
            },
        }

    def get_latest_optimization_snapshot(self) -> dict[str, Any] | None:
        """Expose the latest adaptive optimization using the public API contract."""
        if not self.opt_events:
            return None

        event = self.opt_events[-1]
        schedule_map: dict[str, str] | None = None
        schedule_details: list[dict[str, Any]] = []
        if event.schedule is not None:
            schedule_map = {
                decision.intersection_id: decision.selected_phase.value
                for decision in event.schedule.decisions
                if decision.interval_index == 0
            }
            schedule_details = [
                {
                    "intersection_id": intersection_id,
                    "selected_phase": phase_id,
                    "phase_duration_seconds": 30.0,
                }
                for intersection_id, phase_id in schedule_map.items()
            ]

        return {
            "simulation_id": self.simulation_id,
            "timestamp": event.timestamp,
            "solver_name": event.solver_name,
            "qubo_energy": event.qubo_energy,
            "is_feasible": event.is_feasible,
            "selected_schedule": schedule_map,
            "optimization_time_seconds": event.optimization_time,
            "fallback_used": event.fallback_used,
            "fallback_reason": event.fallback_reason,
            "applied_to_simulation": event.schedule is not None,
            "schedule_details": schedule_details,
            "raw_metrics": {
                "status": event.status,
                "interval_index": event.interval_index,
            },
        }


class SimulationSessionManager:
    """Registry managing active simulation sessions across endpoints."""

    def __init__(self) -> None:
        self._sessions: dict[str, SimulationSession] = {}

    def create_session(
        self,
        simulation_id: str,
        scenario_id: str = "low-traffic",
        duration_seconds: float | None = None,
        control_interval_seconds: float = 5.0,
        seed: int = 42,
        adaptive_enabled: bool = True,
        events_enabled: bool = True,
        emergency_corridor_enabled: bool = True,
    ) -> SimulationSession:
        """Create and store a new simulation session."""
        scenario = get_scenario_by_id(scenario_id, seed=seed)
        session = SimulationSession(
            simulation_id=simulation_id,
            scenario=scenario,
            duration_seconds=duration_seconds,
            control_interval_seconds=control_interval_seconds,
            seed=seed,
            adaptive_enabled=adaptive_enabled,
            events_enabled=events_enabled,
            emergency_corridor_enabled=emergency_corridor_enabled,
        )
        self._sessions[simulation_id] = session
        return session

    def get_session(self, simulation_id: str) -> SimulationSession:
        """Retrieve existing simulation session or raise APIException 404."""
        if simulation_id not in self._sessions:
            raise APIException(
                status_code=404,
                code="SIMULATION_NOT_FOUND",
                message=f"Simulation session '{simulation_id}' does not exist.",
            )
        return self._sessions[simulation_id]

    def remove_session(self, simulation_id: str) -> None:
        """Remove simulation session from registry."""
        if simulation_id in self._sessions:
            del self._sessions[simulation_id]

    def list_sessions(self) -> list[str]:
        """List active simulation session IDs."""
        return list(self._sessions.keys())


# Global singleton instance
session_manager = SimulationSessionManager()
