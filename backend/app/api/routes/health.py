"""Health check endpoint."""

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.hardening.health import check_subsystem_health

health_router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    """Health status response."""

    status: str = Field(default="ok", description="Application status")
    version: str = Field(default="1.0.0", description="API version")
    subsystems: dict[str, Any] = Field(
        default_factory=dict, description="Subsystem availability status"
    )


@health_router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Return backend health status."""
    health_info = check_subsystem_health()
    return HealthResponse(
        status=health_info["status"],
        version="1.0.0",
        subsystems=health_info["subsystems"],
    )
