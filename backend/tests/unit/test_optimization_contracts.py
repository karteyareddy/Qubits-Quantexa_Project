"""Tests for explicit optimization execution and fallback metadata."""

import pytest
from app.domain.optimization import (
    ExecutionClass,
    FeasibilityResult,
    OptimizationPlan,
    OptimizationResult,
    OptimizationType,
    SolverMetadata,
)
from pydantic import ValidationError


def build_plan() -> OptimizationPlan:
    return OptimizationPlan(
        plan_id="plan-1",
        optimization_type=OptimizationType.SIGNAL,
        decisions={"I1": "NS_GREEN"},
    )


@pytest.mark.parametrize(
    ("execution_class", "solver_name"),
    [
        (ExecutionClass.QUANTUM, "qaoa"),
        (ExecutionClass.CLASSICAL, "exact"),
    ],
)
def test_quantum_and_classical_results_are_explicit(
    execution_class: ExecutionClass,
    solver_name: str,
) -> None:
    result = OptimizationResult(
        result_id=f"result-{execution_class.value}",
        optimization_type=OptimizationType.SIGNAL,
        solver=SolverMetadata(
            solver_name=solver_name,
            backend_name="test-backend",
            execution_class=execution_class,
        ),
        objective_value=1.5,
        runtime_ms=12.0,
        feasible=True,
        feasibility=FeasibilityResult(feasible=True),
        decoded_plan=build_plan(),
        selected_bitstring="01",
    )

    assert result.solver.execution_class is execution_class
    assert result.fallback_used is False


def test_classical_fallback_requires_reason() -> None:
    result = OptimizationResult(
        result_id="result-fallback",
        optimization_type=OptimizationType.SIGNAL,
        solver=SolverMetadata(
            solver_name="exact",
            backend_name="local",
            execution_class=ExecutionClass.CLASSICAL_FALLBACK,
        ),
        runtime_ms=5.0,
        feasible=True,
        feasibility=FeasibilityResult(feasible=True),
        fallback_used=True,
        fallback_reason="QAOA backend unavailable",
        decoded_plan=build_plan(),
    )

    assert result.fallback_used is True
    assert result.fallback_reason == "QAOA backend unavailable"

    with pytest.raises(ValidationError, match="fallback reason"):
        OptimizationResult(
            result_id="invalid-fallback",
            optimization_type=OptimizationType.SIGNAL,
            solver=result.solver,
            runtime_ms=5.0,
            feasible=True,
            feasibility=FeasibilityResult(feasible=True),
            fallback_used=True,
            decoded_plan=build_plan(),
        )


def test_feasibility_result_is_internally_consistent() -> None:
    infeasible = FeasibilityResult(feasible=False, violations=("multiple selections",))
    assert infeasible.feasible is False

    with pytest.raises(ValidationError, match="cannot contain violations"):
        FeasibilityResult(feasible=True, violations=("unexpected",))
