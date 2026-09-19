"""Unit tests for exact QUBO energy evaluation."""

from app.signals.qubo.evaluator import evaluate_bitstring_energy, evaluate_qubo_energy


def test_evaluate_qubo_energy_linear_and_quadratic() -> None:
    Q = {
        ("x0", "x0"): -100.0,
        ("x1", "x1"): -100.0,
        ("x0", "x1"): 200.0,
    }
    offset = 100.0

    # x = (0, 0): E = 0 + offset = 100
    assert evaluate_qubo_energy(Q, {"x0": 0, "x1": 0}, offset) == 100.0

    # x = (1, 0): E = -100 + 100 = 0
    assert evaluate_qubo_energy(Q, {"x0": 1, "x1": 0}, offset) == 0.0

    # x = (0, 1): E = -100 + 100 = 0
    assert evaluate_qubo_energy(Q, {"x0": 0, "x1": 1}, offset) == 0.0

    # x = (1, 1): E = -100 - 100 + 200 + 100 = 100
    assert evaluate_qubo_energy(Q, {"x0": 1, "x1": 1}, offset) == 100.0


def test_evaluate_bitstring_energy() -> None:
    Q = {("x0", "x0"): -10.0, ("x1", "x1"): 5.0}
    var_names = ["x0", "x1"]

    assert evaluate_bitstring_energy(Q, "10", var_names, constant_offset=2.0) == -8.0
    assert evaluate_bitstring_energy(Q, "01", var_names, constant_offset=2.0) == 7.0
