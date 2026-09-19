"""Unit tests for reference brute-force Signal QUBO solver."""

from app.domain.signal import SignalPhase
from app.signals.qubo.decoder import decode_signal_qubo_solution
from app.signals.qubo.reference_solver import solve_signal_qubo_brute_force
from app.signals.qubo.variables import create_signal_variables


def test_brute_force_solver_finds_minimum_energy_and_feasible_solution() -> None:
    intersections = ["I1"]
    legal_phases = {"I1": [SignalPhase.EW_GREEN, SignalPhase.NS_GREEN]}
    var_map, var_names = create_signal_variables(intersections, legal_phases, horizon_intervals=1)

    # Hand-crafted QUBO where x_I1_P1_T0=1 gives lowest energy
    Q = {
        ("x_I1_P0_T0", "x_I1_P0_T0"): -100.0 + 50.0,
        ("x_I1_P1_T0", "x_I1_P1_T0"): -100.0 - 20.0,
        ("x_I1_P0_T0", "x_I1_P1_T0"): 200.0,
    }

    best_assignment, min_energy, bitstring = solve_signal_qubo_brute_force(
        Q, var_names, constant_offset=100.0
    )

    assert best_assignment == {"x_I1_P0_T0": 0, "x_I1_P1_T0": 1}
    assert min_energy == -20.0
    assert bitstring == "01"

    schedule, feasibility, _bit = decode_signal_qubo_solution(
        best_assignment, var_map, var_names, legal_phases, horizon_intervals=1
    )
    assert feasibility.feasible is True
    assert schedule is not None
    assert schedule.decisions[0].selected_phase is SignalPhase.NS_GREEN
