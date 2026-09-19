"""Deterministic fixed-time intersection controller."""

from dataclasses import dataclass, field

from app.domain.signal import ApproachSignalState, SignalIndication, SignalPhase, SignalState
from app.signals.models import SignalApproach, SignalTiming
from app.signals.phases import indication_for_phase
from app.signals.timing import phase_schedule, phase_timing_at


@dataclass(frozen=True)
class FixedTimeSignalController:
    intersection_id: str
    approaches: tuple[SignalApproach, ...]
    timing: SignalTiming = field(default_factory=SignalTiming)
    offset_seconds: int = 0

    def __post_init__(self) -> None:
        if self.offset_seconds < 0:
            raise ValueError("signal offset cannot be negative")
        if any(
            approach.intersection_id != self.intersection_id
            for approach in self.approaches
        ):
            raise ValueError("controller approaches must belong to its intersection")
        edge_ids = [approach.incoming_edge_id for approach in self.approaches]
        if len(edge_ids) != len(set(edge_ids)):
            raise ValueError("controller incoming edges must be unique")

    def current_phase(self, time_seconds: float) -> SignalPhase:
        return phase_timing_at(
            time_seconds,
            self.timing,
            offset_seconds=self.offset_seconds,
        ).phase

    def state_at(self, time_seconds: float) -> SignalState:
        phase_timing = phase_timing_at(
            time_seconds,
            self.timing,
            offset_seconds=self.offset_seconds,
        )
        legal_phases = tuple(dict.fromkeys(phase for phase, _ in phase_schedule(self.timing)))
        approach_states = tuple(
            ApproachSignalState(
                approach_id=approach.approach_id,
                incoming_edge_id=approach.incoming_edge_id,
                source_node_id=approach.source_node_id,
                indication=indication_for_phase(approach.axis, phase_timing.phase),
            )
            for approach in self.approaches
        )
        return SignalState(
            intersection_id=self.intersection_id,
            current_phase=phase_timing.phase,
            phase_started_at_seconds=max(
                0.0,
                time_seconds - phase_timing.phase_elapsed_seconds,
            ),
            remaining_time_seconds=phase_timing.phase_remaining_seconds,
            legal_phases=legal_phases,
            phase_elapsed_seconds=phase_timing.phase_elapsed_seconds,
            cycle_position_seconds=phase_timing.cycle_position_seconds,
            cycle_duration_seconds=float(self.timing.cycle_duration_seconds),
            approach_states=approach_states,
        )

    def can_move(self, approach: SignalApproach, time_seconds: float) -> bool:
        if approach not in self.approaches:
            return False
        phase = self.current_phase(time_seconds)
        return indication_for_phase(approach.axis, phase) is SignalIndication.GREEN

    def approach_for_edge(self, incoming_edge_id: str) -> SignalApproach | None:
        return next(
            (
                approach
                for approach in self.approaches
                if approach.incoming_edge_id == incoming_edge_id
            ),
            None,
        )
