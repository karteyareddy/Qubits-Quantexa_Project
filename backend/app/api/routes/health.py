"""Health check endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

health_router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    """Health status response."""

    status: str = Field(default="ok", description="Application status")
    version: str = Field(default="1.0.0", description="API version")


@health_router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Return backend health status."""
    return HealthResponse(status="ok", version="1.0.0")
