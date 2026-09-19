"""Unit tests for local classical refinement of candidate solutions."""

from app.domain.signal import SignalPhase
from app.optimization.hybrid_models import CandidateSolution
from app.optimization.hybrid_refinement import refine_candidate_solution


def test_refine_candidate_solution_improves_or_retains_feasible() -> None:
    # 1 intersection, 2 phases, 1 interval (x0, x1)
    # Q: x0 cost=20, x1 cost=5, penalty=100
    # Feasible states: "10" (E=20), "01" (E=5)
    var_names = ["x_I1_P0_T0", "x_I1_P1_T0"]
    var_map = {("I1", 0, 0): "x_I1_P0_T0", ("I1", 1, 0): "x_I1_P1_T0"}
    legal_phases = {"I1": (SignalPhase.EW_GREEN, SignalPhase.NS_GREEN)}

    Q = {
        ("x_I1_P0_T0", "x_I1_P0_T0"): -100.0 + 20.0,
        ("x_I1_P1_T0", "x_I1_P1_T0"): -100.0 + 5.0,
        ("x_I1_P0_T0", "x_I1_P1_T0"): 200.0,
    }
    offset = 100.0

    # Start with feasible candidate "10" (E=20.0)
    initial_cand = CandidateSolution(
        bitstring="10",
        probability=0.8,
        qubo_energy=20.0,
        is_feasible=True,
        decoded_schedule=None,
    )

    # Note: 1-bit flip from "10" gives "00" (infeasible) or "11" (infeasible).
    # Since 1-bit flips to infeasible states are rejected, "10" remains local minimum under 1-bit flips.
    refined_cand = refine_candidate_solution(
        candidate=initial_cand,
        Q=Q,
        constant_offset=offset,
        variable_names=var_names,
        variable_map=var_map,
        intersection_legal_phases=legal_phases,
        horizon_intervals=1,
    )

    assert refined_cand.is_feasible is True
    assert refined_cand.qubo_energy <= initial_cand.qubo_energy
