"""Optimization request/result contracts without solver behavior."""

from enum import Enum
from typing import Self

from pydantic import Field, JsonValue, model_validator

from app.domain.base import DomainModel, Identifier


class ExecutionClass(str, Enum):
    QUANTUM = "QUANTUM"
    CLASSICAL = "CLASSICAL"
    CLASSICAL_FALLBACK = "CLASSICAL FALLBACK"


class OptimizationType(str, Enum):
    ROUTE = "route"
    SIGNAL = "signal"
    HYBRID = "hybrid"


class SolverMetadata(DomainModel):
    solver_name: Identifier
    backend_name: Identifier
    execution_class: ExecutionClass
    parameters: dict[str, JsonValue] = Field(default_factory=dict)


class FeasibilityResult(DomainModel):
    feasible: bool
    violations: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_violations(self) -> Self:
        if self.feasible and self.violations:
            raise ValueError("feasible results cannot contain violations")
        if not self.feasible and not self.violations:
            raise ValueError("infeasible results require at least one violation")
        return self


class OptimizationPlan(DomainModel):
    plan_id: Identifier
    optimization_type: OptimizationType
    decisions: dict[str, JsonValue]


class OptimizationResult(DomainModel):
    result_id: Identifier
    optimization_type: OptimizationType
    solver: SolverMetadata
    objective_value: float | None = None
    energy: float | None = None
    runtime_ms: float = Field(ge=0.0)
    feasible: bool
    feasibility: FeasibilityResult
    fallback_used: bool = False
    fallback_reason: str | None = None
    decoded_plan: OptimizationPlan | None = None
    selected_bitstring: str | None = Field(default=None, pattern=r"^[01]+$")
    metadata: dict[str, JsonValue] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_execution_metadata(self) -> Self:
        if self.feasible != self.feasibility.feasible:
            raise ValueError("result feasibility fields must agree")
        if self.feasible and self.decoded_plan is None:
            raise ValueError("feasible results require a decoded plan")
        if self.fallback_used:
            if self.solver.execution_class is not ExecutionClass.CLASSICAL_FALLBACK:
                raise ValueError("fallback results must use CLASSICAL FALLBACK execution class")
            if not self.fallback_reason or not self.fallback_reason.strip():
                raise ValueError("fallback results require a fallback reason")
        else:
            if self.solver.execution_class is ExecutionClass.CLASSICAL_FALLBACK:
                raise ValueError("CLASSICAL FALLBACK requires fallback_used=true")
            if self.fallback_reason is not None:
                raise ValueError("non-fallback results cannot include a fallback reason")
        return self
