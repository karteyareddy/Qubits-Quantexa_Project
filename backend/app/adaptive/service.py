"""Closed-Loop Adaptive Traffic Simulation Runner."""

import time

from app.adaptive.config import AdaptiveConfig
from app.adaptive.controller import AdaptiveSignalPolicy
from app.adaptive.models import AdaptiveOptimizationEvent, AdaptiveRunResult
from app.adaptive.observer import TrafficObserver
from app.adaptive.scheduler import AdaptiveScheduler
from app.domain.signal import SignalPhase
from app.metrics.service import MetricsService
from app.optimization.hybrid_solver import HybridSignalOptimizer
from app.signals.policy import SignalSystem
from app.simulation.engine import TrafficSimulation
from app.simulation.models import SimulationScenario, SimulationState


class AdaptiveSimulationRunner:
    """Coordinates closed-loop adaptive simulation execution."""

    def __init__(self, config: AdaptiveConfig | None = None) -> None:
        self.config = config or AdaptiveConfig()

    def run_adaptive_simulation(
        self,
        scenario: SimulationScenario,
        duration_seconds: float | None = None,
        run_id: str = "adaptive-run-1",
    ) -> AdaptiveRunResult:
        """Run complete closed-loop adaptive simulation."""
        cfg = self.config
        requested_duration = duration_seconds if duration_seconds is not None else scenario.duration_seconds

        # 1. Initialize Signal System & Adaptive Entry Policy
        signal_system = SignalSystem.for_network(scenario.network)
        adaptive_policy = AdaptiveSignalPolicy(
            signal_system=signal_system,
            network=scenario.network,
        )

        # 2. Initialize Traffic Simulation Engine
        sim = TrafficSimulation(scenario, entry_policy=adaptive_policy)

        # 3. Initialize Adaptive Control Components
        observer = TrafficObserver()
        scheduler = AdaptiveScheduler(config=cfg)
        hybrid_optimizer = HybridSignalOptimizer(config=cfg.hybrid_config)
        metrics_service = MetricsService()

        observations: list[SimulationState] = []
        events: list[AdaptiveOptimizationEvent] = []
        interval_idx = 0

        # 4. Closed-Loop Execution Loop
        while sim.state.simulation_time_seconds < requested_duration:
            current_time = sim.state.simulation_time_seconds

            # Record state trajectory observation for Stage 6 metrics
            observations.append(sim.state)

            # Check if optimization cycle is due
            if scheduler.is_optimization_due(current_time):
                # Observe traffic snapshot without mutating simulation state
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

                events.append(
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

            # Advance simulation by 1 second
            sim.step()

        # Final state observation
        final_state = sim.state
        observations.append(final_state)

        # 5. Compute Stage 6 Scenario Metrics
        metrics = metrics_service.evaluate(
            scenario_id=scenario.scenario_id,
            final_state=final_state,
            observations=observations,
        )

        total_opt_time = sum(e.optimization_time for e in events)
        avg_opt_time = total_opt_time / len(events) if events else 0.0

        # Collect active signal phases at end of run
        final_signal_states = adaptive_policy.states_at(final_state.simulation_time_seconds)
        final_phases: dict[str, SignalPhase] = {s.intersection_id: s.current_phase for s in final_signal_states}

        return AdaptiveRunResult(
            run_id=run_id,
            duration_seconds=requested_duration,
            control_interval_seconds=cfg.control_interval_seconds,
            optimization_count=len(events),
            optimization_events=tuple(events),
            final_simulation_time=final_state.simulation_time_seconds,
            final_signal_state=final_phases,
            metrics=metrics,
            total_optimization_time=total_opt_time,
            average_optimization_time=avg_opt_time,
        )
