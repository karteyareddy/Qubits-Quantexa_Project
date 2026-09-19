"""Domain exception mapping and HTTP error handlers for FastAPI."""

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.errors import (
    DomainError,
    OptimizationError,
    RouteNotFoundError,
    SimulationError,
)
from app.emergency.models import EmergencyCorridorError
from app.events.models import EventError
from app.hardening.validation import ValidationError

logger = logging.getLogger(__name__)


class APIException(Exception):
    """Base API exception with HTTP status code and error details."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers on FastAPI application instance."""

    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": exc.message,
                }
            },
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "code": "RESOURCE_LIMIT_EXCEEDED",
                    "message": str(exc),
                }
            },
        )

    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "code": exc.code.upper(),
                    "message": str(exc),
                }
            },
        )

    @app.exception_handler(SimulationError)
    async def simulation_error_handler(request: Request, exc: SimulationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "code": "SIMULATION_ERROR",
                    "message": str(exc),
                }
            },
        )

    @app.exception_handler(RouteNotFoundError)
    async def routing_error_handler(request: Request, exc: RouteNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "code": "ROUTING_ERROR",
                    "message": str(exc),
                }
            },
        )

    @app.exception_handler(OptimizationError)
    async def optimization_error_handler(request: Request, exc: OptimizationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "OPTIMIZATION_ERROR",
                    "message": str(exc),
                }
            },
        )

    @app.exception_handler(EventError)
    async def event_error_handler(request: Request, exc: EventError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "code": "EVENT_ERROR",
                    "message": str(exc),
                }
            },
        )

    @app.exception_handler(EmergencyCorridorError)
    async def emergency_corridor_error_handler(
        request: Request, exc: EmergencyCorridorError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "code": "EMERGENCY_CORRIDOR_ERROR",
                    "message": str(exc),
                }
            },
        )

    @app.exception_handler(KeyError)
    async def key_error_handler(request: Request, exc: KeyError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": {
                    "code": "RESOURCE_NOT_FOUND",
                    "message": f"Resource not found: {exc}",
                }
            },
        )
