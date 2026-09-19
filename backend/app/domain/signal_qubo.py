"""Domain models for signal control QUBO optimization and schedules."""

from typing import Self

from pydantic import Field, model_validator

from app.domain.base import DomainModel, Identifier
from app.domain.optimization import FeasibilityResult
from app.domain.signal import SignalPhase


class IntervalSignalDecision(DomainModel):
    """Signal phase assignment for one intersection during one time interval."""

    intersection_id: Identifier
    interval_index: int = Field(ge=0)
    selected_phase: SignalPhase
    phase_index: int = Field(ge=0)


class SignalSchedule(DomainModel):
    """Multi-intersection multi-interval signal schedule decoded from QUBO solution."""

    schedule_id: Identifier
    horizon_intervals: int = Field(ge=1)
    interval_duration_seconds: float = Field(gt=0.0)
    decisions: tuple[IntervalSignalDecision, ...] = ()

    def get_decision(
        self, intersection_id: str, interval_index: int
    ) -> IntervalSignalDecision | None:
        """Find decision for a specific intersection and interval index."""
        for d in self.decisions:
            if (
                d.intersection_id == intersection_id
                and d.interval_index == interval_index
            ):
                return d
        return None


class SignalQuboResult(DomainModel):
    """Typed result from constructing and evaluating a Signal Control QUBO."""

    result_id: Identifier
    num_intersections: int = Field(ge=0)
    horizon_intervals: int = Field(ge=1)
    num_variables: int = Field(ge=0)
    num_linear_terms: int = Field(ge=0)
    num_quadratic_terms: int = Field(ge=0)
    constant_offset: float = 0.0
    energy: float = 0.0
    feasible: bool = True
    feasibility: FeasibilityResult
    decoded_schedule: SignalSchedule | None = None
    selected_bitstring: str = Field(pattern=r"^[01]+$")
    variable_names: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_feasibility(self) -> Self:
        if self.feasible != self.feasibility.feasible:
            raise ValueError("feasible fields must agree")
        if self.feasible and self.decoded_schedule is None:
            raise ValueError("feasible results require a decoded schedule")
        return self
