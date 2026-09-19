"""AdaptiveSignalPolicy integrating optimized SignalSchedules with TrafficSimulation."""

from dataclasses import dataclass, field

from app.domain.network import Network, NetworkEdge
from app.domain.signal import SignalPhase, SignalState
from app.domain.signal_qubo import SignalSchedule
from app.domain.vehicle import Vehicle
from app.signals.models import ApproachAxis
from app.signals.phases import _approach_axis
from app.signals.policy import SignalSystem
from app.simulation.models import SimulationState


@dataclass
class AdaptiveSignalPolicy:
    """Entry policy applying optimized SignalSchedules and emergency preemption overrides to simulation intersections."""

    signal_system: SignalSystem
    network: Network
    active_schedule: SignalSchedule | None = None
    schedule_applied_time: float = 0.0
    preemption_overrides: dict[str, SignalPhase] = field(default_factory=dict)
    _node_map: dict[str, str] = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        self._node_by_id = {node.node_id: node for node in self.network.nodes}

    def update_schedule(self, schedule: SignalSchedule, applied_time: float) -> None:
        """Update active signal schedule applied at applied_time."""
        self.active_schedule = schedule
        self.schedule_applied_time = applied_time

    def set_preemption_overrides(self, overrides: dict[str, SignalPhase]) -> None:
        """Set active signal preemption overrides for emergency green corridors."""
        self.preemption_overrides = dict(overrides)

    def clear_preemption_overrides(self) -> None:
        """Clear active signal preemption overrides."""
        self.preemption_overrides.clear()

    def can_enter_next_edge(
        self,
        vehicle: Vehicle,
        next_edge: NetworkEdge,
        state: SimulationState,
        at_time_seconds: float,
    ) -> bool:
        """Evaluate permission for vehicle to enter next_edge at at_time_seconds."""
        incoming_edge_id = vehicle.current_edge_id
        if incoming_edge_id is None:
            return True

        intersection_id = next_edge.source
        intersection_node = self._node_by_id.get(intersection_id)
        if intersection_node is None or not intersection_node.is_intersection:
            return True

        # 1. Check emergency preemption overrides
        if intersection_id in self.preemption_overrides:
            override_phase = self.preemption_overrides[intersection_id]
            incoming_edge = next((e for e in self.network.edges if e.edge_id == incoming_edge_id), None)
            if incoming_edge is not None:
                source_node = self._node_by_id[incoming_edge.source]
                axis = _approach_axis(source_node, intersection_node, fallback_index=0)
                if override_phase == SignalPhase.EW_GREEN:
                    return axis == ApproachAxis.EAST_WEST
                elif override_phase == SignalPhase.NS_GREEN:
                    return axis == ApproachAxis.NORTH_SOUTH

        # 2. Check active optimized schedule
        sched = self.active_schedule
        if sched is not None:
            elapsed = at_time_seconds - self.schedule_applied_time
            if elapsed >= 0.0:
                interval_idx = int(elapsed // sched.interval_duration_seconds)
                if interval_idx < sched.horizon_intervals:
                    decision = sched.get_decision(intersection_id, interval_idx)
                    if decision is not None:
                        incoming_edge = next((e for e in self.network.edges if e.edge_id == incoming_edge_id), None)
                        if incoming_edge is not None:
                            source_node = self._node_by_id[incoming_edge.source]
                            axis = _approach_axis(source_node, intersection_node, fallback_index=0)

                            if decision.selected_phase == SignalPhase.EW_GREEN:
                                return axis == ApproachAxis.EAST_WEST
                            elif decision.selected_phase == SignalPhase.NS_GREEN:
                                return axis == ApproachAxis.NORTH_SOUTH

        # Fallback to underlying fixed-time signal system
        return self.signal_system.can_move(intersection_id, incoming_edge_id, at_time_seconds)

    def states_at(self, time_seconds: float) -> tuple[SignalState, ...]:
        """Return active SignalState for each controlled intersection."""
        base_states: list[SignalState] = []

        sched = self.active_schedule
        if sched is not None:
            elapsed = time_seconds - self.schedule_applied_time
            if elapsed >= 0.0:
                interval_idx = int(elapsed // sched.interval_duration_seconds)
                if interval_idx < sched.horizon_intervals:
                    intersections = sorted(
                        node.node_id for node in self.network.nodes if node.is_intersection
                    )
                    for i_id in intersections:
                        decision = sched.get_decision(i_id, interval_idx)
                        phase = decision.selected_phase if decision else SignalPhase.NS_GREEN
                        interval_elapsed = elapsed % sched.interval_duration_seconds
                        rem_time = max(0.0, sched.interval_duration_seconds - interval_elapsed)
                        base_states.append(
                            SignalState(
                                intersection_id=i_id,
                                current_phase=phase,
                                phase_started_at_seconds=self.schedule_applied_time + (interval_idx * sched.interval_duration_seconds),
                                remaining_time_seconds=rem_time,
                                legal_phases=(SignalPhase.EW_GREEN, SignalPhase.NS_GREEN),
                                phase_elapsed_seconds=interval_elapsed,
                                cycle_position_seconds=interval_elapsed,
                                cycle_duration_seconds=sched.interval_duration_seconds,
                            )
                        )

        if not base_states:
            base_states = list(self.signal_system.states_at(time_seconds))

        if self.preemption_overrides:
            updated_states: list[SignalState] = []
            for state in base_states:
                if state.intersection_id in self.preemption_overrides:
                    updated_states.append(
                        state.model_copy(
                            update={"current_phase": self.preemption_overrides[state.intersection_id]}
                        )
                    )
                else:
                    updated_states.append(state)
            return tuple(updated_states)

        return tuple(base_states)
