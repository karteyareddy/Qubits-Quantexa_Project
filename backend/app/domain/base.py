"""Shared primitives for backend domain contracts."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

Identifier = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class DomainModel(BaseModel):
    """Base model with strict external-data handling."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)
