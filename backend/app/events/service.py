"""Dynamic simulation service integrating events into closed-loop adaptive control."""

import time
from typing import Any

from pydantic import Field

from app.adaptive.config import AdaptiveConfig
from app.adaptive.controller import AdaptiveSignalPolicy
from app.adaptive.models import AdaptiveOptimizationEvent, AdaptiveRunResult
from app.adaptive.observer import TrafficObserver
from app.adaptive.scheduler import AdaptiveScheduler
from app.domain.base import DomainModel
from app.events.engine import EventEngine
from app.events.models import EventRecord
from app.metrics.service import MetricsService
from app.optimization.hybrid_solver import HybridSignalOptimizer
from app.signals.policy import SignalSystem
from app.simulation.engine import TrafficSimulation
from app.simulation.models import SimulationScenario, SimulationState


class DynamicRunResult(DomainModel):
    """Execution results for a dynamic adaptive traffic simulation."""

    adaptive_result: AdaptiveRunResult
    event_history: tuple[EventRecord, ...]
    event_metrics: dict[str, Any] = Field(default_factory=dict)


class DynamicSimulationRunner:
    """Runs closed-loop adaptive simulation with dynamic event processing."""

    def __init__(
        self,
        adaptive_config: AdaptiveConfig | None = None,
        event_engine: EventEngine | None = None,
    ) -> None:
        self.adaptive_config = adaptive_config or AdaptiveConfig()
        self.event_engine = event_engine or EventEngine()

    def run_dynamic_simulation(
        self,
        scenario: SimulationScenario,
        events: list[Any] | None = None,
        duration_seconds: float | None = None,
        run_id: str = "dynamic-adaptive-run-1",
    ) -> DynamicRunResult:
        """Run complete dynamic adaptive traffic simulation."""
        cfg = self.adaptive_config
        requested_duration = (
            duration_seconds if duration_seconds is not None else scenario.duration_seconds
        )

        # Schedule initial events if provided
        if events:
            for event in events:
                self.event_engine.scheduler.add_event(event)

        # 1. Initialize Signal System & Adaptive Policy
        signal_system = SignalSystem.for_network(scenario.network)
        adaptive_policy = AdaptiveSignalPolicy(
            signal_system=signal_system,
            network=scenario.network,
        )

        # 2. Initialize Traffic Simulation Engine
        sim = TrafficSimulation(scenario, entry_policy=adaptive_policy)

        # 3. Initialize Adaptive Components
        observer = TrafficObserver()
        scheduler = AdaptiveScheduler(config=cfg)
        hybrid_optimizer = HybridSignalOptimizer(config=cfg.hybrid_config)
        metrics_service = MetricsService()

        observations: list[SimulationState] = []
        opt_events: list[AdaptiveOptimizationEvent] = []
        interval_idx = 0

        # 4. Dynamic Execution Loop
        while sim.state.simulation_time_seconds < requested_duration:
            current_time = sim.state.simulation_time_seconds

            # Step 4a: Apply events due at current simulation time
            self.event_engine.process_due_events(sim)

            # Step 4b: Record observation
            observations.append(sim.state)

            # Step 4c: Check if optimization cycle is due
            if scheduler.is_optimization_due(current_time):
                net_snap, state_snap = observer.observe(sim)

                opt_start = time.perf_counter()
                opt_res = hybrid_optimizer.optimize(net_snap, state_snap)
                opt_time = time.perf_counter() - opt_start

                status = opt_res.status
                schedule = None

                if opt_res.is_feasible and opt_res.selected_schedule is not None:
                    schedule = opt_res.selected_schedule
                    adaptive_policy.update_schedule(schedule, current_time)
                else:
                    if cfg.fail_on_optimization_error:
                        raise RuntimeError(f"Adaptive optimization failed at t={current_time}")
                    status = "retained_previous"

                opt_events.append(
                    AdaptiveOptimizationEvent(
                        timestamp=current_time,
                        interval_index=interval_idx,
                        status=status,
                        solver_name=opt_res.solver_name,
                        qubo_energy=opt_res.selected_energy,
                        is_feasible=opt_res.is_feasible,
                        schedule=schedule,
                        optimization_time=opt_time,
                        fallback_used=opt_res.fallback_used,
                        fallback_reason=opt_res.fallback_reason,
                    )
                )

                scheduler.mark_optimized(current_time)
                interval_idx += 1

            # Step 4d: Advance simulation by 1 timestep
            sim.step()

            # Step 4e: Check event expirations at updated time
            self.event_engine.check_expirations(sim)

        # Calculate final metrics trajectory
        scenario_metrics = metrics_service.evaluate(
            scenario.scenario_id,
            sim.state,
            observations=observations,
        )

        # Collect active signal phases at end of run
        final_signal_states = adaptive_policy.states_at(sim.state.simulation_time_seconds)
        final_phases = {s.intersection_id: s.current_phase for s in final_signal_states}

        total_opt_time = sum(e.optimization_time for e in opt_events)
        avg_opt_time = total_opt_time / len(opt_events) if opt_events else 0.0

        adaptive_result = AdaptiveRunResult(
            run_id=run_id,
            duration_seconds=requested_duration,
            control_interval_seconds=cfg.control_interval_seconds,
            optimization_count=len(opt_events),
            optimization_events=tuple(opt_events),
            final_simulation_time=sim.state.simulation_time_seconds,
            final_signal_state=final_phases,
            metrics=scenario_metrics,
            total_optimization_time=total_opt_time,
            average_optimization_time=avg_opt_time,
        )

        return DynamicRunResult(
            adaptive_result=adaptive_result,
            event_history=self.event_engine.history,
            event_metrics=self.event_engine.get_event_metrics(),
        )
