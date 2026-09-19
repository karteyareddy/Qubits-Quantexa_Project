"""Traffic, environmental, and emergency metric contracts."""

from pydantic import Field

from app.domain.base import DomainModel


class EnvironmentalMetrics(DomainModel):
    """Transparent environmental estimates; formulas are added later."""

    fuel_liters_estimate: float = Field(ge=0.0)
    co2_kg_estimate: float = Field(ge=0.0)


class EmergencyMetrics(DomainModel):
    emergency_travel_time_seconds: float | None = Field(default=None, ge=0.0)
    emergency_completed: bool | None = None


class TrafficMetrics(DomainModel):
    """Metrics sampled from a future simulation tick or experiment."""

    simulation_time_seconds: float = Field(ge=0.0)
    average_wait_seconds: float = Field(ge=0.0)
    total_wait_seconds: float = Field(ge=0.0)
    queue_length: int = Field(ge=0)
    maximum_queue_length: int = Field(ge=0)
    throughput: int = Field(ge=0)
    average_travel_time_seconds: float = Field(ge=0.0)
    congestion: float = Field(ge=0.0)
    environmental: EnvironmentalMetrics
    emergency: EmergencyMetrics
