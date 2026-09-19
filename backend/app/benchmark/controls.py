"""Traffic control strategies for benchmark evaluation."""

from abc import ABC, abstractmethod
from typing import Any

from app.adaptive.controller import AdaptiveSignalPolicy
from app.adaptive.observer import TrafficObserver
from app.domain.signal_qubo import SignalSchedule
from app.emergency.service import EmergencyCorridorService
from app.events.engine import EventEngine
from app.events.models import TrafficEventBase
from app.optimization.hybrid_solver import HybridSignalOptimizer
from app.signals.policy import FixedTimeSignalPolicy, SignalSystem
from app.simulation.engine import TrafficSimulation
from app.simulation.models import SimulationScenario, SimulationState


class TrafficControlStrategy(ABC):
    """Abstract interface for benchmark traffic control strategies."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Strategy identifier (e.g. fixed_time or hybrid_qaoa)."""

    @abstractmethod
    def run_simulation(
        self,
        scenario: SimulationScenario,
        events: tuple[TrafficEventBase, ...] = (),
        control_interval_seconds: float = 5.0,
    ) -> tuple[TrafficSimulation, list[SimulationState], EmergencyCorridorService, dict[str, Any]]:
        """Execute simulation under this strategy and return engine, observations trajectory, emergency service, and optimization stats."""


class FixedTimeStrategy(TrafficControlStrategy):
    """Classical Fixed-Time Signal Control Strategy (Stage 5 Baseline)."""

    @property
    def name(self) -> str:
        return "fixed_time"

    def run_simulation(
        self,
        scenario: SimulationScenario,
        events: tuple[TrafficEventBase, ...] = (),
        control_interval_seconds: float = 5.0,
    ) -> tuple[TrafficSimulation, list[SimulationState], EmergencyCorridorService, dict[str, Any]]:
        # Initialize classical signal system & entry policy
        signal_system = SignalSystem.for_network(scenario.network)
        fixed_policy = FixedTimeSignalPolicy(signal_system=signal_system)

        # Initialize event engine and emergency corridor service
        event_engine = EventEngine()
        for ev in events:
            event_engine.scheduler.add_event(ev)

        emergency_service = EmergencyCorridorService()

        # Create simulation engine
        sim = TrafficSimulation(scenario, entry_policy=fixed_policy)

        observations: list[SimulationState] = []

        # Main simulation loop
        while sim.state.simulation_time_seconds < scenario.duration_seconds:
            observations.append(sim.state)

            # Process due dynamic events & step emergency corridors
            event_engine.process_due_events(sim)
            emergency_service.update(sim, signal_system=signal_system, adaptive_policy=None)

            # Advance simulation by 1s
            sim.step(1.0)

        observations.append(sim.state)

        stats: dict[str, Any] = {
            "optimization_count": 0,
            "qaoa_runtime_seconds": 0.0,
            "hybrid_runtime_seconds": 0.0,
            "fallback_count": 0,
            "feasibility_rate": 1.0,
            "average_qubo_energy": None,
        }

        return sim, observations, emergency_service, stats


class HybridQuantumStrategy(TrafficControlStrategy):
    """Hybrid QAOA Quantum-Classical Signal Optimization Strategy (Stage 10/11/14)."""

    def __init__(
        self,
        optimizer: HybridSignalOptimizer | None = None,
    ) -> None:
        self.optimizer = optimizer or HybridSignalOptimizer()

    @property
    def name(self) -> str:
        return "hybrid_qaoa"

    def run_simulation(
        self,
        scenario: SimulationScenario,
        events: tuple[TrafficEventBase, ...] = (),
        control_interval_seconds: float = 5.0,
    ) -> tuple[TrafficSimulation, list[SimulationState], EmergencyCorridorService, dict[str, Any]]:
        # Initialize base fixed-time signal policy and adaptive policy wrapper
        signal_system = SignalSystem.for_network(scenario.network)
        adaptive_policy = AdaptiveSignalPolicy(
            signal_system=signal_system, network=scenario.network
        )

        observer = TrafficObserver()
        event_engine = EventEngine()
        for ev in events:
            event_engine.scheduler.add_event(ev)

        emergency_service = EmergencyCorridorService()

        sim = TrafficSimulation(scenario, entry_policy=adaptive_policy)

        observations: list[SimulationState] = []
        last_opt_time = -control_interval_seconds
        opt_count = 0
        fallback_count = 0
        feasible_count = 0
        total_qubo_energy = 0.0
        energies_recorded = 0

        while sim.state.simulation_time_seconds < scenario.duration_seconds:
            current_time = sim.state.simulation_time_seconds
            observations.append(sim.state)

            # Process due dynamic events & step emergency corridors
            event_engine.process_due_events(sim)
            emergency_service.update(
                sim, signal_system=signal_system, adaptive_policy=adaptive_policy
            )

            # Run hybrid optimization at configured control intervals
            if current_time - last_opt_time >= control_interval_seconds:
                net_snap, state_snap = observer.observe(sim)
                opt_res = self.optimizer.optimize(net_snap, state_snap)
                opt_count += 1

                if opt_res.fallback_used:
                    fallback_count += 1
                if opt_res.is_feasible:
                    feasible_count += 1
                if opt_res.selected_energy is not None:
                    total_qubo_energy += opt_res.selected_energy
                    energies_recorded += 1

                if opt_res.is_feasible and opt_res.selected_schedule is not None:
                    sel_sched = opt_res.selected_schedule
                    if isinstance(sel_sched, SignalSchedule):
                        adaptive_policy.update_schedule(sel_sched, current_time)

                last_opt_time = current_time

            # Step simulation engine
            sim.step(1.0)

        observations.append(sim.state)

        stats = {
            "optimization_count": opt_count,
            "fallback_count": fallback_count,
            "feasibility_rate": (feasible_count / opt_count) if opt_count > 0 else 0.0,
            "average_qubo_energy": (total_qubo_energy / energies_recorded) if energies_recorded > 0 else None,
            "solver_name": "hybrid_qaoa",
        }

        return sim, observations, emergency_service, stats
