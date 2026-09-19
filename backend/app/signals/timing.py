"""Pure fixed-cycle timing calculations."""

from dataclasses import dataclass

from app.domain.signal import SignalPhase
from app.signals.models import SignalTiming


@dataclass(frozen=True)
class PhaseTimingState:
    phase: SignalPhase
    cycle_position_seconds: float
    phase_elapsed_seconds: float
    phase_remaining_seconds: float


def phase_timing_at(
    time_seconds: float,
    timing: SignalTiming,
    *,
    offset_seconds: int = 0,
) -> PhaseTimingState:
    """Return the same phase for every equivalent cycle position."""
    if time_seconds < 0:
        raise ValueError("signal time cannot be negative")
    if offset_seconds < 0:
        raise ValueError("signal offset cannot be negative")
    cycle_duration = timing.cycle_duration_seconds
    cycle_position = (time_seconds + offset_seconds) % cycle_duration
    elapsed_before_phase = 0.0
    for phase, duration in phase_schedule(timing):
        phase_end = elapsed_before_phase + duration
        if cycle_position < phase_end:
            elapsed = cycle_position - elapsed_before_phase
            return PhaseTimingState(
                phase=phase,
                cycle_position_seconds=cycle_position,
                phase_elapsed_seconds=elapsed,
                phase_remaining_seconds=duration - elapsed,
            )
        elapsed_before_phase = phase_end
    raise RuntimeError("signal cycle did not resolve a phase")


def phase_schedule(timing: SignalTiming) -> tuple[tuple[SignalPhase, int], ...]:
    schedule: list[tuple[SignalPhase, int]] = [
        (SignalPhase.EW_GREEN, timing.green_seconds),
        (SignalPhase.EW_YELLOW, timing.yellow_seconds),
    ]
    if timing.all_red_seconds:
        schedule.append((SignalPhase.ALL_RED, timing.all_red_seconds))
    schedule.extend(
        (
            (SignalPhase.NS_GREEN, timing.green_seconds),
            (SignalPhase.NS_YELLOW, timing.yellow_seconds),
        )
    )
    if timing.all_red_seconds:
        schedule.append((SignalPhase.ALL_RED, timing.all_red_seconds))
    return tuple(schedule)
