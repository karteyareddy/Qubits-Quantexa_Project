"""Typed traffic, environmental, emergency, and scenario metric results."""

from typing import Literal, Self

from pydantic import Field, model_validator

from app.domain.base import DomainModel, Identifier


class VehicleMetrics(DomainModel):
    vehicle_id: Identifier
    completed: bool
    travel_time_seconds: float | None = Field(default=None, ge=0.0)
    waiting_time_seconds: float = Field(ge=0.0)
    emergency: bool


class EdgeTrafficMetrics(DomainModel):
    edge_id: Identifier
    occupancy: int = Field(ge=0)
    queue_length: int = Field(ge=0)
    waiting_vehicle_ids: tuple[Identifier, ...] = ()


class IntersectionApproachMetrics(DomainModel):
    approach_id: Identifier
    queue_length: int = Field(ge=0)
    waiting_vehicle_ids: tuple[Identifier, ...] = ()


class EnvironmentalMetrics(DomainModel):
    """Prototype estimates derived from configurable rate assumptions."""

    fuel_liters: float = Field(ge=0.0)
    co2_kg: float = Field(ge=0.0)
    fuel_liters_per_vehicle: float = Field(ge=0.0)
    co2_kg_per_vehicle: float = Field(ge=0.0)
    moving_fuel_liters: float = Field(ge=0.0)
    idle_fuel_liters: float = Field(ge=0.0)
    is_estimate: Literal[True] = True


class EmergencyMetrics(DomainModel):
    emergency_total: int = Field(ge=0)
    emergency_completed: int = Field(ge=0)
    emergency_active: int = Field(ge=0)
    emergency_completion_rate: float = Field(ge=0.0, le=1.0)
    emergency_total_waiting_seconds: float = Field(ge=0.0)
    emergency_average_waiting_seconds: float = Field(ge=0.0)
    emergency_average_travel_seconds: float = Field(ge=0.0)

    @model_validator(mode="after")
    def validate_counts(self) -> Self:
        if self.emergency_total != self.emergency_completed + self.emergency_active:
            raise ValueError("emergency total must equal completed plus active")
        return self


class TrafficMetrics(DomainModel):
    """Traffic outcomes measured independently from any controller or optimizer."""

    simulation_duration_seconds: float = Field(ge=0.0)
    total_vehicles: int = Field(ge=0)
    completed_vehicles: int = Field(ge=0)
    active_vehicles: int = Field(ge=0)
    completion_rate: float = Field(ge=0.0, le=1.0)
    throughput: int = Field(ge=0)
    throughput_per_minute: float = Field(ge=0.0)
    total_waiting_seconds: float = Field(ge=0.0)
    average_waiting_seconds: float = Field(ge=0.0)
    max_waiting_seconds: float = Field(ge=0.0)
    average_travel_seconds: float = Field(ge=0.0)
    max_travel_seconds: float = Field(ge=0.0)
    max_queue_length: int = Field(ge=0)
    final_queue_length: int = Field(ge=0)
    average_queue_length: float = Field(ge=0.0)
    per_vehicle: tuple[VehicleMetrics, ...] = ()
    edges: tuple[EdgeTrafficMetrics, ...] = ()
    intersection_approaches: tuple[IntersectionApproachMetrics, ...] = ()

    @model_validator(mode="after")
    def validate_counts(self) -> Self:
        if self.total_vehicles != self.completed_vehicles + self.active_vehicles:
            raise ValueError("total vehicles must equal completed plus active")
        if self.throughput != self.completed_vehicles:
            raise ValueError("throughput must equal completed vehicles")
        if len(self.per_vehicle) != self.total_vehicles:
            raise ValueError("per-vehicle results must cover every spawned vehicle")
        return self


class ScenarioMetrics(DomainModel):
    scenario_id: Identifier
    simulation_duration_seconds: float = Field(ge=0.0)
    traffic_metrics: TrafficMetrics
    environmental_metrics: EnvironmentalMetrics
    emergency_metrics: EmergencyMetrics
