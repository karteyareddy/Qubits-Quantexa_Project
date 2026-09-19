"""Top-level scenario contracts."""

from typing import Self

from pydantic import Field, model_validator

from app.domain.base import DomainModel, Identifier
from app.domain.event import TrafficEvent
from app.domain.network import Network
from app.domain.signal import SignalState
from app.domain.vehicle import Vehicle


class ScenarioConfiguration(DomainModel):
    tick_seconds: float = Field(default=5.0, gt=0.0)
    optimization_interval_seconds: float = Field(default=30.0, gt=0.0)
    max_vehicles: int = Field(default=1000, ge=1)


class Scenario(DomainModel):
    """Serializable scenario state shared by future services."""

    scenario_id: Identifier
    seed: int
    duration_seconds: float = Field(gt=0.0)
    simulation_time_seconds: float = Field(default=0.0, ge=0.0)
    network: Network
    vehicles: tuple[Vehicle, ...] = ()
    signals: tuple[SignalState, ...] = ()
    events: tuple[TrafficEvent, ...] = ()
    configuration: ScenarioConfiguration = Field(default_factory=ScenarioConfiguration)

    @model_validator(mode="after")
    def validate_references(self) -> Self:
        if self.simulation_time_seconds > self.duration_seconds:
            raise ValueError("simulation time cannot exceed scenario duration")

        node_ids = {node.node_id for node in self.network.nodes}
        vehicle_ids = [vehicle.vehicle_id for vehicle in self.vehicles]
        if len(vehicle_ids) != len(set(vehicle_ids)):
            raise ValueError("vehicle identifiers must be unique")
        for vehicle in self.vehicles:
            if vehicle.origin not in node_ids or vehicle.destination not in node_ids:
                raise ValueError("vehicle endpoints must exist in the scenario network")

        signal_ids = [signal.intersection_id for signal in self.signals]
        if len(signal_ids) != len(set(signal_ids)):
            raise ValueError("signal intersection identifiers must be unique")
        if not set(signal_ids).issubset(node_ids):
            raise ValueError("signals must reference scenario network nodes")

        event_ids = [event.event_id for event in self.events]
        if len(event_ids) != len(set(event_ids)):
            raise ValueError("event identifiers must be unique")
        return self
