"""Unit tests for AdaptiveSignalPolicy schedule application and safety fallback."""

from app.adaptive.controller import AdaptiveSignalPolicy
from app.domain.signal import SignalPhase
from app.domain.signal_qubo import IntervalSignalDecision, SignalSchedule
from app.routing.demo_network import build_demo_network
from app.signals.policy import SignalSystem


def test_adaptive_signal_policy_schedule_application() -> None:
    network = build_demo_network()
    system = SignalSystem.for_network(network)
    policy = AdaptiveSignalPolicy(signal_system=system, network=network)

    # Initially falls back to signal_system states
    base_states = policy.states_at(0.0)
    assert len(base_states) == 6

    # Create active schedule setting I1 to NS_GREEN at interval 0
    decision = IntervalSignalDecision(
        intersection_id="I1",
        interval_index=0,
        selected_phase=SignalPhase.NS_GREEN,
        phase_index=1,
    )
    schedule = SignalSchedule(
        schedule_id="sched-1",
        horizon_intervals=2,
        interval_duration_seconds=10.0,
        decisions=(decision,),
    )

    policy.update_schedule(schedule, applied_time=0.0)

    states_now = policy.states_at(5.0)
    i1_state = next(s for s in states_now if s.intersection_id == "I1")
    assert i1_state.current_phase == SignalPhase.NS_GREEN
