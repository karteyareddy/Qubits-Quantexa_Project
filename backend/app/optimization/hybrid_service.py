"""High-level Hybrid Quantum-Classical Signal Optimization Service."""

from app.domain.network import Network
from app.domain.signal import SignalPhase
from app.optimization.hybrid_models import (
    HybridOptimizationResult,
    HybridOptimizerConfig,
)
from app.optimization.hybrid_solver import HybridSignalOptimizer
from app.simulation.models import SimulationState


def solve_hybrid_signal_optimization(
    network: Network,
    simulation_state: SimulationState,
    config: HybridOptimizerConfig | None = None,
    current_phases: dict[str, SignalPhase] | None = None,
) -> HybridOptimizationResult:
    """Convenience service function running Hybrid Signal Optimization on simulation snapshot.

    Returns:
        HybridOptimizationResult containing candidate distribution, local refinement status,
        and final selected SignalSchedule.
    """
    optimizer = HybridSignalOptimizer(config=config)
    return optimizer.optimize(network, simulation_state, current_phases=current_phases)
