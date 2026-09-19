"""Main FastAPI application construction and router assembly."""

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.errors import register_exception_handlers
from app.api.routes.benchmark import benchmark_router
from app.api.routes.emergency import emergency_router
from app.api.routes.events import events_router
from app.api.routes.health import health_router
from app.api.routes.metrics import metrics_router
from app.api.routes.network import network_router
from app.api.routes.optimization import optimization_router
from app.api.routes.scenarios import scenarios_router
from app.api.routes.simulations import simulations_router
from app.api.routes.ws import ws_router


def create_app() -> FastAPI:
    """Build and configure the main FastAPI application."""
    app = FastAPI(
        title="Quantum-Enhanced Adaptive Urban Traffic Optimization API",
        description=(
            "REST and WebSocket API providing live deterministic traffic simulation, "
            "QAOA hybrid signal optimization, dynamic event injection, and emergency green corridors."
        ),
        version="1.0.0",
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    # Configure CORS for browser compatibility
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register error handlers
    register_exception_handlers(app)

    # Register health router outside /api/v1
    app.include_router(health_router)

    # Assemble versioned API router
    api_v1_router = APIRouter(prefix="/api/v1")
    api_v1_router.include_router(network_router)
    api_v1_router.include_router(scenarios_router)
    api_v1_router.include_router(simulations_router)
    api_v1_router.include_router(optimization_router)
    api_v1_router.include_router(events_router)
    api_v1_router.include_router(emergency_router)
    api_v1_router.include_router(metrics_router)
    api_v1_router.include_router(benchmark_router)
    api_v1_router.include_router(ws_router)

    app.include_router(api_v1_router)

    return app


app = create_app()
