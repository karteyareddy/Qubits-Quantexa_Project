"""Unit tests for fixed-time signal timing and approach safety."""

import pytest
from app.domain.signal import SignalIndication, SignalPhase
from app.routing.demo_network import build_demo_network
from app.signals.models import ApproachAxis, SignalTiming
from app.signals.phases import approaches_for_network
from app.signals.policy import SignalSystem
from app.signals.timing import phase_timing_at


def test_signal_indications_are_explicit() -> None:
    assert set(SignalIndication) == {
        SignalIndication.RED,
        SignalIndication.YELLOW,
        SignalIndication.GREEN,
    }


@pytest.mark.parametrize(
    ("time_seconds", "expected_phase"),
    (
        (0.0, SignalPhase.EW_GREEN),
        (1.0, SignalPhase.EW_GREEN),
        (2.0, SignalPhase.EW_YELLOW),
        (3.0, SignalPhase.ALL_RED),
        (4.0, SignalPhase.NS_GREEN),
        (6.0, SignalPhase.NS_YELLOW),
        (7.0, SignalPhase.ALL_RED),
    ),
)
def test_phase_timing_boundaries(
    time_seconds: float,
    expected_phase: SignalPhase,
) -> None:
    timing = SignalTiming(green_seconds=2, yellow_seconds=1, all_red_seconds=1)

    assert phase_timing_at(time_seconds, timing).phase is expected_phase


def test_cycle_wraps_to_equivalent_state() -> None:
    timing = SignalTiming(green_seconds=2, yellow_seconds=1, all_red_seconds=1)

    initial = phase_timing_at(0.5, timing)
    wrapped = phase_timing_at(0.5 + timing.cycle_duration_seconds, timing)

    assert initial == wrapped


def test_demo_approaches_come_from_incoming_directed_edges() -> None:
    approaches = approaches_for_network(build_demo_network())
    i2 = {approach.incoming_edge_id: approach for approach in approaches["I2"]}

    assert set(i2) == {"I1->I2", "I3->I2", "I5->I2"}
    assert i2["I1->I2"].axis is ApproachAxis.EAST_WEST
    assert i2["I3->I2"].axis is ApproachAxis.EAST_WEST
    assert i2["I5->I2"].axis is ApproachAxis.NORTH_SOUTH
    assert {len(items) for items in approaches.values()} == {2, 3}


def test_conflicting_axes_are_never_permitted_together() -> None:
    timing = SignalTiming(green_seconds=2, yellow_seconds=1, all_red_seconds=1)
    system = SignalSystem.for_network(build_demo_network(), timing=timing)
    controller = system.controllers["I2"]
    east_west = controller.approach_for_edge("I1->I2")
    north_south = controller.approach_for_edge("I5->I2")

    assert east_west is not None
    assert north_south is not None
    for time_seconds in range(timing.cycle_duration_seconds):
        assert not (
            controller.can_move(east_west, float(time_seconds))
            and controller.can_move(north_south, float(time_seconds))
        )


def test_signal_snapshot_is_serializable_and_reports_approaches() -> None:
    system = SignalSystem.for_network(build_demo_network())

    payload = system.controllers["I2"].state_at(0.0).model_dump(mode="json")

    assert payload["current_phase"] == "EW_GREEN"
    assert payload["cycle_position_seconds"] == 0.0
    assert payload["cycle_duration_seconds"] == 48.0
    assert len(payload["approach_states"]) == 3
    assert {state["indication"] for state in payload["approach_states"]} == {
        "RED",
        "GREEN",
    }
