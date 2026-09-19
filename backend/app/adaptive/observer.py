"""TrafficObserver extracting immutable traffic state snapshots for optimization."""

from app.domain.network import Network
from app.simulation.engine import TrafficSimulation
from app.simulation.models import SimulationState


class TrafficObserver:
    """Extracts immutable optimization snapshot from TrafficSimulation without mutating state."""

    def observe(self, simulation: TrafficSimulation) -> tuple[Network, SimulationState]:
        """Return (network, state_snapshot) tuple.

        Guarantees that simulation internal state remains unmutated.
        """
        # Network is immutable; state property returns Pydantic copy
        network = simulation.scenario.network
        state_snapshot = simulation.state.model_copy(deep=True)
        return network, state_snapshot
