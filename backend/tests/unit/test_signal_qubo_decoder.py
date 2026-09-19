"""Unit tests for Signal QUBO decoder and feasibility checks."""

from app.domain.signal import SignalPhase
from app.signals.qubo.decoder import decode_signal_qubo_solution
from app.signals.qubo.variables import create_signal_variables


def test_decode_valid_signal_qubo_assignment() -> None:
    intersections = ["I1"]
    legal_phases = {"I1": [SignalPhase.EW_GREEN, SignalPhase.NS_GREEN]}
    var_map, var_names = create_signal_variables(intersections, legal_phases, horizon_intervals=1)

    # Valid one-hot assignment: P0=1, P1=0
    assignment = {"x_I1_P0_T0": 1, "x_I1_P1_T0": 0}

    schedule, feasibility, bitstring = decode_signal_qubo_solution(
        assignment,
        var_map,
        var_names,
        legal_phases,
        horizon_intervals=1,
    )

    assert feasibility.feasible is True
    assert schedule is not None
    assert len(schedule.decisions) == 1
    assert schedule.decisions[0].intersection_id == "I1"
    assert schedule.decisions[0].selected_phase is SignalPhase.EW_GREEN
    assert bitstring == "10"


def test_decode_invalid_signal_qubo_assignment() -> None:
    intersections = ["I1"]
    legal_phases = {"I1": [SignalPhase.EW_GREEN, SignalPhase.NS_GREEN]}
    var_map, var_names = create_signal_variables(intersections, legal_phases, horizon_intervals=1)

    # Infeasible assignment: both selected (P0=1, P1=1)
    assignment = {"x_I1_P0_T0": 1, "x_I1_P1_T0": 1}

    schedule, feasibility, _bitstring = decode_signal_qubo_solution(
        assignment,
        var_map,
        var_names,
        legal_phases,
        horizon_intervals=1,
    )

    assert feasibility.feasible is False
    assert schedule is None
    assert len(feasibility.violations) == 1
