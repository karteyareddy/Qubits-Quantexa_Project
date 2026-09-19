"""Configuration parameters for Signal-Control QUBO formulation."""

from pydantic import Field

from app.domain.base import DomainModel


class SignalQuboConfig(DomainModel):
    """Configurable weights, penalties, and horizon parameters for Signal QUBO."""

    horizon_intervals: int = Field(default=1, ge=1)
    interval_seconds: float = Field(default=10.0, gt=0.0)
    constraint_penalty: float = Field(default=100.0, ge=0.0)
    queue_weight: float = Field(default=2.0, ge=0.0)
    waiting_weight: float = Field(default=1.0, ge=0.0)
    throughput_weight: float = Field(default=1.5, ge=0.0)
    emergency_weight: float = Field(default=20.0, ge=0.0)
    switch_weight: float = Field(default=5.0, ge=0.0)
    capacity_per_interval_veh: float = Field(default=5.0, ge=0.1)
