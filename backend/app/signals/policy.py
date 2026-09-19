"""Network-wide fixed-time signal policy for simulation integration."""

from dataclasses import dataclass

from app.domain.network import Network, NetworkEdge
from app.domain.signal import SignalState
from app.domain.vehicle import Vehicle
from app.signals.controller import FixedTimeSignalController
from app.signals.models import SignalTiming
from app.signals.phases import approaches_for_network
from app.simulation.models import SimulationState


@dataclass(frozen=True)
class SignalSystem:
    controllers: dict[str, FixedTimeSignalController]

    @classmethod
    def for_network(
        cls,
        network: Network,
        *,
        timing: SignalTiming | None = None,
        offset_seconds: int = 0,
    ) -> "SignalSystem":
        configured_timing = timing or SignalTiming()
        approaches = approaches_for_network(network)
        return cls(
            controllers={
                intersection_id: FixedTimeSignalController(
                    intersection_id=intersection_id,
                    approaches=intersection_approaches,
                    timing=configured_timing,
                    offset_seconds=offset_seconds,
                )
                for intersection_id, intersection_approaches in sorted(approaches.items())
            }
        )

    def state_at(self, intersection_id: str, time_seconds: float) -> SignalState | None:
        controller = self.controllers.get(intersection_id)
        return controller.state_at(time_seconds) if controller is not None else None

    def states_at(self, time_seconds: float) -> tuple[SignalState, ...]:
        return tuple(
            controller.state_at(time_seconds)
            for _, controller in sorted(self.controllers.items())
        )

    def can_move(
        self,
        intersection_id: str,
        incoming_edge_id: str,
        time_seconds: float,
    ) -> bool:
        controller = self.controllers.get(intersection_id)
        if controller is None:
            return True
        approach = controller.approach_for_edge(incoming_edge_id)
        return approach is not None and controller.can_move(approach, time_seconds)


@dataclass(frozen=True)
class FixedTimeSignalPolicy:
    """Adapt fixed-time controllers to the simulation entry-policy protocol."""

    signal_system: SignalSystem

    def can_enter_next_edge(
        self,
        vehicle: Vehicle,
        next_edge: NetworkEdge,
        state: SimulationState,
        at_time_seconds: float,
    ) -> bool:
        if vehicle.current_edge_id is None:
            return True
        return self.signal_system.can_move(
            next_edge.source,
            vehicle.current_edge_id,
            at_time_seconds,
        )

    def states_at(self, time_seconds: float) -> tuple[SignalState, ...]:
        return self.signal_system.states_at(time_seconds)
