"""Traffic-signal state contracts."""

from enum import Enum
from typing import Self

from pydantic import Field, model_validator

from app.domain.base import DomainModel, Identifier


class SignalPhase(str, Enum):
    NS_GREEN = "NS_GREEN"
    EW_GREEN = "EW_GREEN"
    NS_YELLOW = "NS_YELLOW"
    EW_YELLOW = "EW_YELLOW"
    YELLOW = "YELLOW"
    ALL_RED = "ALL_RED"


class SignalIndication(str, Enum):
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"


class ApproachSignalState(DomainModel):
    approach_id: Identifier
    incoming_edge_id: Identifier
    source_node_id: Identifier
    indication: SignalIndication


class SignalState(DomainModel):
    """Serializable intersection signal snapshot."""

    intersection_id: Identifier
    current_phase: SignalPhase
    phase_started_at_seconds: float = Field(ge=0.0)
    remaining_time_seconds: float = Field(ge=0.0)
    legal_phases: tuple[SignalPhase, ...] = Field(min_length=1)
    phase_elapsed_seconds: float = Field(default=0.0, ge=0.0)
    cycle_position_seconds: float = Field(default=0.0, ge=0.0)
    cycle_duration_seconds: float = Field(default=0.0, ge=0.0)
    approach_states: tuple[ApproachSignalState, ...] = ()

    @model_validator(mode="after")
    def validate_current_phase(self) -> Self:
        if self.current_phase not in self.legal_phases:
            raise ValueError("current phase must be included in legal phases")
        if len(self.legal_phases) != len(set(self.legal_phases)):
            raise ValueError("legal phases must be unique")
        return self
