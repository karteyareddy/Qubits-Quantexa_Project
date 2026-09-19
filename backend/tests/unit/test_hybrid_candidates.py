"""Unit tests for top-K candidate extraction and deterministic sorting."""

from app.domain.signal import SignalPhase
from app.optimization.hybrid_candidates import extract_candidates


def test_extract_candidates_aggregation_and_sorting() -> None:
    # 1 intersection, 2 phases, 1 interval (2 variables x0, x1)
    # x0="x_I1_P0_T0", x1="x_I1_P1_T0"
    var_names = ["x_I1_P0_T0", "x_I1_P1_T0"]
    var_map = {("I1", 0, 0): "x_I1_P0_T0", ("I1", 1, 0): "x_I1_P1_T0"}
    legal_phases = {"I1": (SignalPhase.EW_GREEN, SignalPhase.NS_GREEN)}

    # Q = -100 x0 - 100 x1 + 200 x0 x1 + 100
    Q = {
        ("x_I1_P0_T0", "x_I1_P0_T0"): -100.0,
        ("x_I1_P1_T0", "x_I1_P1_T0"): -100.0,
        ("x_I1_P0_T0", "x_I1_P1_T0"): 200.0,
    }
    offset = 100.0

    # Qiskit big-endian measurement counts:
    # '01' -> std '10' (x0=1, x1=0) -> feasible, E=0.0
    # '10' -> std '01' (x0=0, x1=1) -> feasible, E=0.0
    # '11' -> std '11' (x0=1, x1=1) -> infeasible, E=100.0
    counts = {
        "01": 500,
        "10": 300,
        "11": 200,
    }

    candidates = extract_candidates(
        measurement_counts=counts,
        Q=Q,
        constant_offset=offset,
        variable_names=var_names,
        variable_map=var_map,
        intersection_legal_phases=legal_phases,
        horizon_intervals=1,
        top_k=5,
    )

    assert len(candidates) == 3
    # Feasible candidates come first
    assert candidates[0].is_feasible is True
    assert candidates[1].is_feasible is True
    assert candidates[2].is_feasible is False

    # For equal energy (0.0), higher probability comes first:
    # std '10' prob=0.5 > std '01' prob=0.3
    assert candidates[0].bitstring == "10"
    assert abs(candidates[0].probability - 0.5) < 1e-6
    assert candidates[1].bitstring == "01"
    assert abs(candidates[1].probability - 0.3) < 1e-6
