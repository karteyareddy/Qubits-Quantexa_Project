"""Traffic-signal state contracts."""

from enum import Enum
from typing import Self

from pydantic import Field, model_validator

from app.domain.base import DomainModel, Identifier


class SignalPhase(str, Enum):
    NS_GREEN = "NS_GREEN"
    EW_GREEN = "EW_GREEN"
    YELLOW = "YELLOW"
    ALL_RED = "ALL_RED"


class SignalState(DomainModel):
    """Signal state only; transition behavior belongs to Stage 5."""

    intersection_id: Identifier
    current_phase: SignalPhase
    phase_started_at_seconds: float = Field(ge=0.0)
    remaining_time_seconds: float = Field(ge=0.0)
    legal_phases: tuple[SignalPhase, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_current_phase(self) -> Self:
        if self.current_phase not in self.legal_phases:
            raise ValueError("current phase must be included in legal phases")
        if len(self.legal_phases) != len(set(self.legal_phases)):
            raise ValueError("legal phases must be unique")
        return self
