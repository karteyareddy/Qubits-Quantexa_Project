"""Execution runner for deterministic hackathon demonstration narrative."""

import logging
import uuid

from app.adaptive.config import AdaptiveConfig
from app.adaptive.controller import AdaptiveSignalPolicy
from app.adaptive.observer import TrafficObserver
from app.adaptive.scheduler import AdaptiveScheduler
from app.demo.config import DEFAULT_DEMO_CONFIG, DemoConfig
from app.demo.models import (
    DemoExecutionResult,
    DemoNarrativeMilestone,
)
from app.demo.scenario import build_demo_scenario
from app.emergency.service import EmergencyCorridorService
from app.events.engine import EventEngine
from app.hardening.determinism import seed_all
from app.metrics.service import MetricsService
from app.optimization.hybrid_solver import HybridSignalOptimizer
from app.signals.policy import SignalSystem
from app.simulation.engine import TrafficSimulation
from app.simulation.models import SimulationState

logger = logging.getLogger(__name__)


class DemoRunner:
    """Orchestrates end-to-end deterministic demonstration lifecycle."""

    def __init__(self, metrics_service: MetricsService | None = None) -> None:
        self.metrics_service = metrics_service or MetricsService()

    def run_demo(self, config: DemoConfig | None = None) -> DemoExecutionResult:
        """Run the complete presentation narrative and return structured milestone summary."""
        cfg = config or DEFAULT_DEMO_CONFIG
        seed_all(cfg.seed)

        demo_id = f"demo-{uuid.uuid4().hex[:6]}"
        scenario, events = build_demo_scenario(
            seed=cfg.seed,
            duration_seconds=cfg.duration_seconds,
        )

        signal_system = SignalSystem.for_network(scenario.network)
        adaptive_policy = AdaptiveSignalPolicy(
            signal_system=signal_system,
            network=scenario.network,
        )
        sim = TrafficSimulation(scenario, entry_policy=adaptive_policy)

        adaptive_cfg = AdaptiveConfig(control_interval_seconds=cfg.control_interval_seconds)
        observer = TrafficObserver()
        scheduler = AdaptiveScheduler(config=adaptive_cfg)
        optimizer = HybridSignalOptimizer(config=adaptive_cfg.hybrid_config)
        event_engine = EventEngine()
        emergency_service = EmergencyCorridorService()

        # Schedule narrative events into event engine
        for ev in events:
            event_engine.scheduler.add_event(ev)

        milestones: list[DemoNarrativeMilestone] = []
        observations: list[SimulationState] = []
        optimizations_count = 0
        last_solver_name = "none"

        # Record initial milestone
        milestones.append(
            DemoNarrativeMilestone(
                timestamp_seconds=0.0,
                milestone_id="m1_init",
                title="Simulation Initialized",
                description="6-intersection network initialized with baseline traffic demand.",
                subsystem="simulation",
                details={"active_vehicles": len(sim.state.active_vehicles)},
            )
        )

        dt = scenario.configuration.timestep_seconds
        total_steps = int(cfg.duration_seconds / dt)

        for step_idx in range(total_steps):
            current_time = sim.state.simulation_time_seconds

            # 1. Process due events
            if cfg.enable_events:
                due_records = event_engine.process_due_events(sim)
                for rec in due_records:
                    milestones.append(
                        DemoNarrativeMilestone(
                            timestamp_seconds=current_time,
                            milestone_id=f"m_evt_{rec.event_id}",
                            title=f"Dynamic Event Triggered: {rec.event_type.value}",
                            description=f"Event applied to target '{rec.target}'.",
                            subsystem="events",
                            details={"event_id": rec.event_id, "target": rec.target},
                        )
                    )

            # 2. Update emergency corridors
            if cfg.enable_emergency_corridor:
                emergency_service.update(
                    sim,
                    signal_system=signal_system,
                    adaptive_policy=adaptive_policy,
                )
                if emergency_service.active_corridors:
                    active_c = emergency_service.active_corridors[0]
                    if not any(m.milestone_id == f"m_emerg_{active_c.corridor_id}" for m in milestones):
                        milestones.append(
                            DemoNarrativeMilestone(
                                timestamp_seconds=current_time,
                                milestone_id=f"m_emerg_{active_c.corridor_id}",
                                title="Emergency Green Corridor Activated",
                                description=f"Signal preemption granted for vehicle '{active_c.vehicle_id}'.",
                                subsystem="emergency",
                                details={
                                    "corridor_id": active_c.corridor_id,
                                    "intersections": [i.intersection_id for i in active_c.intersections],
                                },
                            )
                        )

            # 3. Record observation
            observations.append(sim.state)

            # 4. Adaptive optimization check
            if cfg.enable_qaoa and scheduler.is_optimization_due(current_time):
                net_snap, state_snap = observer.observe(sim)
                opt_res = optimizer.optimize(net_snap, state_snap)
                optimizations_count += 1
                last_solver_name = opt_res.solver_name

                if opt_res.is_feasible and opt_res.selected_schedule is not None:
                    adaptive_policy.update_schedule(opt_res.selected_schedule, current_time)

                milestones.append(
                    DemoNarrativeMilestone(
                        timestamp_seconds=current_time,
                        milestone_id=f"m_opt_{step_idx}",
                        title="Hybrid QAOA Optimization Executed",
                        description=f"Solver '{opt_res.solver_name}' computed schedule. Feasible: {opt_res.is_feasible}.",
                        subsystem="optimization",
                        details={
                            "solver_name": opt_res.solver_name,
                            "is_feasible": opt_res.is_feasible,
                            "qubo_energy": opt_res.selected_energy,
                            "fallback_used": opt_res.fallback_used,
                        },
                    )
                )
                scheduler.mark_optimized(current_time)

            # 5. Advance simulation step
            sim.step()

            # 6. Expiration check after step
            if cfg.enable_events:
                event_engine.check_expirations(sim)

        # Final metrics evaluation
        final_metrics = self.metrics_service.evaluate(
            scenario_id=cfg.scenario_id,
            final_state=sim.state,
            observations=observations,
        )

        tm = final_metrics.traffic_metrics
        em = final_metrics.environmental_metrics

        milestones.append(
            DemoNarrativeMilestone(
                timestamp_seconds=sim.state.simulation_time_seconds,
                milestone_id="m_final",
                title="Demo Simulation Completed",
                description="Evaluation completed across baseline, QAOA, dynamic events, and emergency corridor.",
                subsystem="metrics",
                details={
                    "total_vehicles": tm.total_vehicles,
                    "completed_vehicles": tm.completed_vehicles,
                    "average_waiting_time": tm.average_waiting_seconds,
                    "co2_emitted": em.co2_kg,
                },
            )
        )

        return DemoExecutionResult(
            demo_id=demo_id,
            status="COMPLETED",
            duration_seconds=sim.state.simulation_time_seconds,
            seed=cfg.seed,
            total_vehicles_spawned=tm.total_vehicles,
            total_vehicles_completed=tm.completed_vehicles,
            average_waiting_time_seconds=tm.average_waiting_seconds,
            total_co2_emitted_kg=em.co2_kg,
            optimizations_count=optimizations_count,
            qaoa_solver_name=last_solver_name,
            milestones=milestones,
        )
