"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.router import router

app = FastAPI(title="Quantum Traffic Optimizer")
app.include_router(router)
