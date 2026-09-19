"""Common API schemas and error structures."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class APIErrorDetails(BaseModel):
    """Structured error message details."""

    code: str = Field(..., description="Error code string, e.g. SIMULATION_NOT_FOUND")
    message: str = Field(..., description="Human readable description of the error")
    details: dict[str, Any] | None = Field(default=None, description="Optional detail key-values")


class APIErrorResponse(BaseModel):
    """Standard error response format."""

    error: APIErrorDetails


class StatusResponse(BaseModel):
    """Simple status confirmation response."""

    status: str = Field(default="ok", description="Status result string")
    message: str | None = Field(default=None, description="Optional details")


class GenericResponse(BaseModel, Generic[T]):
    """Generic payload wrapper."""

    success: bool = True
    data: T
