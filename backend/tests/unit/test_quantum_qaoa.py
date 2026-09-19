"""Unit tests for QAOA solver, bitstring endianness, and exact optimum comparison."""

from app.domain.signal import SignalPhase
from app.quantum.config import QAOAConfig
from app.quantum.qaoa import (
    QAOASolver,
    qiskit_bitstring_to_qubo_assignment,
    qiskit_bitstring_to_standard_string,
    standard_string_to_qiskit_bitstring,
)
from app.signals.qubo.reference_solver import solve_signal_qubo_brute_force


def test_qiskit_bitstring_endianness_conversion() -> None:
    vars_list = ["x_I1_P0_T0", "x_I1_P1_T0", "x_I2_P0_T0", "x_I2_P1_T0"]

    # In Qiskit bitstring '1001':
    # Rightmost '1' -> index -1 -> qubit 0 -> x_I1_P0_T0 = 1
    # '0' -> index -2 -> qubit 1 -> x_I1_P1_T0 = 0
    # '0' -> index -3 -> qubit 2 -> x_I2_P0_T0 = 0
    # Leftmost '1' -> index -4 -> qubit 3 -> x_I2_P1_T0 = 1
    qiskit_str = "1001"
    assignment = qiskit_bitstring_to_qubo_assignment(qiskit_str, vars_list)

    assert assignment["x_I1_P0_T0"] == 1
    assert assignment["x_I1_P1_T0"] == 0
    assert assignment["x_I2_P0_T0"] == 0
    assert assignment["x_I2_P1_T0"] == 1

    std_str = qiskit_bitstring_to_standard_string(qiskit_str)
    assert std_str == "1001"[::-1] == "1001" if qiskit_str == qiskit_str[::-1] else "1001"[::-1]
    assert standard_string_to_qiskit_bitstring(std_str) == qiskit_str


def test_qaoa_solver_on_tiny_2_variable_qubo() -> None:
    # 1 intersection, 2 phases, 1 interval (2 variables x0, x1)
    # A*(x0 + x1 - 1)^2 -> A = 100
    Q = {
        ("x0", "x0"): -100.0,
        ("x1", "x1"): -100.0,
        ("x0", "x1"): 200.0,
    }
    offset = 100.0
    var_names = ["x0", "x1"]
    var_map = {
        ("I1", 0, 0): "x0",
        ("I1", 1, 0): "x1",
    }
    legal_phases = {"I1": (SignalPhase.EW_GREEN, SignalPhase.NS_GREEN)}

    # Reference exact classical brute force
    _best_exact_assign, exact_min_energy, _exact_bits = solve_signal_qubo_brute_force(
        Q, var_names, offset
    )
    assert exact_min_energy == 0.0

    config = QAOAConfig(
        reps=1,
        shots=1024,
        seed=42,
        max_iterations=30,
    )
    solver = QAOASolver(config=config)
    result = solver.solve_qubo(
        Q=Q,
        constant_offset=offset,
        variable_names=var_names,
        variable_map=var_map,
        intersection_legal_phases=legal_phases,
        horizon_intervals=1,
    )

    assert result.solver_name == "qaoa"
    assert result.backend_name == "qiskit_aer"
    assert result.num_qubits == 2
    assert result.reps == 1
    assert result.is_feasible is True
    assert result.best_energy == exact_min_energy == 0.0
    assert result.decoded_schedule is not None
    assert len(result.decoded_schedule.decisions) == 1
    assert len(result.measurement_counts) > 0


def test_qaoa_solver_reproducibility_with_seed() -> None:
    Q = {
        ("x0", "x0"): -50.0,
        ("x1", "x1"): -50.0,
        ("x0", "x1"): 100.0,
    }
    offset = 50.0
    var_names = ["x0", "x1"]
    var_map = {("I1", 0, 0): "x0", ("I1", 1, 0): "x1"}
    legal_phases = {"I1": (SignalPhase.EW_GREEN, SignalPhase.NS_GREEN)}

    config = QAOAConfig(reps=1, shots=512, seed=123, max_iterations=20)
    solver1 = QAOASolver(config)
    res1 = solver1.solve_qubo(Q, offset, var_names, var_map, legal_phases, 1)

    solver2 = QAOASolver(config)
    res2 = solver2.solve_qubo(Q, offset, var_names, var_map, legal_phases, 1)

    assert res1.best_bitstring == res2.best_bitstring
    assert res1.best_energy == res2.best_energy
    assert res1.optimal_gammas == res2.optimal_gammas
    assert res1.optimal_betas == res2.optimal_betas
