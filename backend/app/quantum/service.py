"""High-level QAOA Signal Optimization Service."""

from app.domain.network import Network
from app.quantum.config import QAOAConfig
from app.quantum.models import QAOAResult
from app.quantum.qaoa import QAOASolver
from app.signals.qubo.builder import SignalQuboBuilder
from app.signals.qubo.config import SignalQuboConfig
from app.simulation.models import SimulationState


def solve_signal_qubo_with_qaoa(
    network: Network,
    simulation_state: SimulationState,
    qubo_config: SignalQuboConfig | None = None,
    qaoa_config: QAOAConfig | None = None,
) -> QAOAResult:
    """Build Stage 8 Signal-Control QUBO from simulation snapshot and solve with Stage 9 QAOA.

    Returns:
        QAOAResult containing best bitstring, energy, feasibility status, and decoded schedule.
    """
    q_cfg = qubo_config or SignalQuboConfig()
    builder = SignalQuboBuilder(config=q_cfg)
    Q, off, var_names, var_map = builder.build_qubo(network, simulation_state)

    solver = QAOASolver(config=qaoa_config)
    return solver.solve_qubo(
        Q=Q,
        constant_offset=off,
        variable_names=var_names,
        variable_map=var_map,
        horizon_intervals=q_cfg.horizon_intervals,
    )
