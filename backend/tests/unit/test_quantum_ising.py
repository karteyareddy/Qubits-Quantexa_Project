"""Unit tests for QUBO to Ising spin conversion and energy equivalence."""

from app.quantum.ising import ising_energy, qubo_to_ising
from app.signals.qubo.evaluator import evaluate_qubo_energy


def test_hand_checkable_1_intersection_2_phase_qubo_to_ising_conversion() -> None:
    # 2 variables x0, x1 with constraint penalty A=100: A*(x0 + x1 - 1)^2
    # E_QUBO(x) = -100 x0 - 100 x1 + 200 x0 x1 + 100
    Q = {
        ("x0", "x0"): -100.0,
        ("x1", "x1"): -100.0,
        ("x0", "x1"): 200.0,
    }
    offset = 100.0
    vars_list = ["x0", "x1"]

    h, J, c_ising = qubo_to_ising(Q, offset, vars_list)

    # Verify linear Z terms and quadratic ZZ interaction
    # x0 = (1 - z0)/2, x1 = (1 - z1)/2
    # E_QUBO = -100(1-z0)/2 - 100(1-z1)/2 + 200(1-z0)(1-z1)/4 + 100
    #        = -50 + 50z0 - 50 + 50z1 + 50(1 - z0 - z1 + z0 z1) + 100
    #        = 50 z0 z1 + 50
    # Thus h0=0, h1=0, J(0,1)=50, c_ising=50
    assert abs(c_ising - 50.0) < 1e-9
    assert abs(J.get((0, 1), 0.0) - 50.0) < 1e-9
    assert 0 not in h or abs(h[0]) < 1e-9

    # Exhaustive 2^2 verification of E_QUBO(x) == E_Ising(z)
    for bit0 in (0, 1):
        for bit1 in (0, 1):
            assignment = {"x0": bit0, "x1": bit1}
            qubo_e = evaluate_qubo_energy(Q, assignment, offset)

            z0 = 1 - 2 * bit0
            z1 = 1 - 2 * bit1
            is_e = ising_energy(h, J, c_ising, [z0, z1])

            assert abs(qubo_e - is_e) < 1e-9


def test_exhaustive_qubo_to_ising_equivalence_4_variables() -> None:
    # 4 variables with arbitrary linear and quadratic coefficients
    vars_list = [f"x{i}" for i in range(4)]
    Q = {
        ("x0", "x0"): -10.0,
        ("x1", "x1"): 5.0,
        ("x2", "x2"): -8.0,
        ("x3", "x3"): 12.0,
        ("x0", "x1"): 15.0,
        ("x1", "x2"): -6.0,
        ("x2", "x3"): 20.0,
        ("x0", "x3"): 4.0,
    }
    offset = 42.0

    h, J, c_ising = qubo_to_ising(Q, offset, vars_list)

    # Exhaustive 2^4 = 16 assignments check
    for b0 in (0, 1):
        for b1 in (0, 1):
            for b2 in (0, 1):
                for b3 in (0, 1):
                    x_bits = [b0, b1, b2, b3]
                    assignment = {vars_list[i]: x_bits[i] for i in range(4)}
                    qubo_e = evaluate_qubo_energy(Q, assignment, offset)

                    z_vec = [1 - 2 * b for b in x_bits]
                    is_e = ising_energy(h, J, c_ising, z_vec)

                    assert abs(qubo_e - is_e) < 1e-9
