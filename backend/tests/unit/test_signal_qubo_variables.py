"""Unit tests for Signal QUBO decision variable mapping and parsing."""

from app.domain.signal import SignalPhase
from app.signals.qubo.variables import (
    create_signal_variables,
    parse_signal_variable_name,
)


def test_create_signal_variables_indexing() -> None:
    intersections = ["I1", "I2"]
    legal_phases = {
        "I1": [SignalPhase.EW_GREEN, SignalPhase.NS_GREEN],
        "I2": [SignalPhase.EW_GREEN, SignalPhase.NS_GREEN],
    }

    var_map, var_names = create_signal_variables(
        intersections, legal_phases, horizon_intervals=2
    )

    assert len(var_names) == 8  # 2 intersections * 2 phases * 2 intervals
    assert var_map[("I1", 0, 0)] == "x_I1_P0_T0"
    assert var_map[("I1", 1, 0)] == "x_I1_P1_T0"
    assert var_map[("I1", 0, 1)] == "x_I1_P0_T1"
    assert var_map[("I2", 0, 0)] == "x_I2_P0_T0"


def test_parse_signal_variable_name() -> None:
    assert parse_signal_variable_name("x_I1_P0_T0") == ("I1", 0, 0)
    assert parse_signal_variable_name("x_I5_P1_T2") == ("I5", 1, 2)
    assert parse_signal_variable_name("invalid") is None
    assert parse_signal_variable_name("x_I1_invalid") is None
