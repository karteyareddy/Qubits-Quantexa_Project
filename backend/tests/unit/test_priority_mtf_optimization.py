"""Unit tests for Stage 7 Priority-Aware MTF optimization components."""

from app.domain.optimization import ExecutionClass
from app.domain.vehicle import EmergencySubtype, Vehicle, VehicleType
from app.optimization.decoder import decode_subproblem_solution
from app.optimization.priority_mtf import decompose_into_subproblems
from app.optimization.qubo import build_bqm, build_cost_hamiltonian
from app.optimization.solver import solve_qubo
from app.optimization.variables import create_subproblem_variables, parse_variable_name


def test_variable_creation_and_parsing() -> None:
    v1 = _vehicle("v1")
    v2 = _vehicle("v2")
    candidate_map = {
        "v1": (("I1", "I2"), ("I1", "I4", "I2")),
        "v2": (("I2", "I3"),),
    }

    var_map = create_subproblem_variables([v1, v2], candidate_map)

    assert var_map[("v1", 0)] == "x_v1_0"
    assert var_map[("v1", 1)] == "x_v1_1"
    assert var_map[("v2", 0)] == "x_v2_0"
    assert parse_variable_name("x_v1_0") == ("v1", 0)
    assert parse_variable_name("invalid") is None


def test_emergency_vehicles_grouped_in_first_subproblem() -> None:
    em = _vehicle("em1", emergency=True)
    r1 = _vehicle("r1")
    r2 = _vehicle("r2")

    subproblems = decompose_into_subproblems([r1, em, r2], max_subproblem_size=1)

    assert len(subproblems) == 3
    assert subproblems[0][0].vehicle_id == "em1"
    assert {subproblems[1][0].vehicle_id, subproblems[2][0].vehicle_id} == {"r1", "r2"}


def test_qubo_construction_and_bqm() -> None:
    v1 = _vehicle("v1")
    candidate_map = {"v1": (("I1", "I2"), ("I1", "I4", "I2"))}
    var_map = create_subproblem_variables([v1], candidate_map)
    edge_costs = {("I1", "I2"): 10.0, ("I1", "I4"): 5.0, ("I4", "I2"): 5.0}

    Q = build_cost_hamiltonian([v1], var_map, candidate_map, edge_costs)
    bqm = build_bqm(Q)

    assert bqm.num_variables == 2
    assert ("x_v1_0", "x_v1_0") in Q
    assert ("x_v1_1", "x_v1_1") in Q


def test_solver_fallback_metadata_is_explicit() -> None:
    v1 = _vehicle("v1")
    candidate_map = {"v1": (("I1", "I2"),)}
    var_map = create_subproblem_variables([v1], candidate_map)
    edge_costs = {("I1", "I2"): 10.0}
    Q = build_cost_hamiltonian([v1], var_map, candidate_map, edge_costs)
    bqm = build_bqm(Q)

    sample, _energy, meta, fallback_used, reason = solve_qubo(bqm, method="exact")
    assert meta.solver_name == "exact"
    assert meta.execution_class is ExecutionClass.CLASSICAL
    assert fallback_used is False
    assert reason is None
    assert sample.get("x_v1_0") == 1

    _sample_f, _energy_f, meta_f, fallback_used_f, _reason_f = solve_qubo(
        bqm, method="invalid_method"
    )
    assert meta_f.solver_name == "dimod_sa"
    assert meta_f.execution_class is ExecutionClass.CLASSICAL
    assert fallback_used_f is False


def test_decoder_handles_valid_and_violating_samples() -> None:
    v1 = _vehicle("v1")
    candidate_map = {"v1": (("I1", "I2"), ("I1", "I4", "I2"))}
    var_map = create_subproblem_variables([v1], candidate_map)

    # Valid selection
    sample_valid = {"x_v1_0": 1, "x_v1_1": 0}
    routes, _idx, feasibility, _bit = decode_subproblem_solution(
        sample_valid, var_map, [v1], candidate_map
    )
    assert feasibility.feasible is True
    assert routes["v1"] == ("I1", "I2")

    # Infeasible selection (multiple ones)
    sample_invalid = {"x_v1_0": 1, "x_v1_1": 1}
    _routes_inv, _idx_inv, feasibility_inv, _bit_inv = decode_subproblem_solution(
        sample_invalid, var_map, [v1], candidate_map
    )
    assert feasibility_inv.feasible is False
    assert len(feasibility_inv.violations) == 1


def _vehicle(
    vid: str,
    *,
    emergency: bool = False,
    priority: int = 1,
) -> Vehicle:
    return Vehicle(
        vehicle_id=vid,
        vehicle_type=VehicleType.EMERGENCY if emergency else VehicleType.REGULAR,
        origin="I1",
        destination="I2",
        is_emergency=emergency,
        emergency_subtype=EmergencySubtype.AMBULANCE if emergency else None,
        priority_weight=10 if emergency else priority,
    )
