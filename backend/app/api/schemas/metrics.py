"""API schemas for simulation metrics endpoints."""

from typing import Any

from pydantic import BaseModel, Field


class SimulationMetricsResponse(BaseModel):
    """Metrics snapshot response."""

    simulation_id: str
    simulation_time_seconds: float
    total_vehicles: int
    active_vehicles: int
    arrived_vehicles: int
    completion_rate: float
    throughput_vph: float
    average_travel_time_seconds: float
    average_waiting_time_seconds: float
    total_fuel_consumed_liters: float
    total_co2_emitted_kg: float
    emergency_waiting_time_seconds: float
    emergency_travel_time_seconds: float
    emergency_corridor_active: bool
    event_impact_summary: dict[str, Any] = Field(default_factory=dict)
    optimization_summary: dict[str, Any] = Field(default_factory=dict)
