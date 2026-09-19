"""Serializable contracts for deterministic traffic simulation."""

from typing import Self

from pydantic import ConfigDict, Field, model_validator

from app.domain.base import DomainModel, Identifier
from app.domain.network import Network
from app.domain.vehicle import Vehicle, VehicleState


class SimulationConfiguration(DomainModel):
    """Runtime limits for the lightweight discrete-time engine."""

    timestep_seconds: float = Field(default=1.0, gt=0.0)


class ScheduledArrival(DomainModel):
    """A routed vehicle scheduled to enter the simulation."""

    arrival_time_seconds: float = Field(ge=0.0)
    vehicle: Vehicle

    @model_validator(mode="after")
    def validate_vehicle(self) -> Self:
        if self.vehicle.route is None:
            raise ValueError("scheduled vehicles require a route")
        if self.vehicle.state is not VehicleState.PENDING:
            raise ValueError("scheduled vehicles must initially be pending")
        if self.vehicle.arrival_time_seconds != self.arrival_time_seconds:
            raise ValueError("arrival and vehicle arrival times must agree")
        return self


class SimulationScenario(DomainModel):
    """Validated immutable inputs for one reproducible simulation run."""

    scenario_id: Identifier
    seed: int
    duration_seconds: float = Field(gt=0.0)
    network: Network
    arrivals: tuple[ScheduledArrival, ...]
    configuration: SimulationConfiguration = Field(default_factory=SimulationConfiguration)

    @model_validator(mode="after")
    def validate_arrivals(self) -> Self:
        node_ids = {node.node_id for node in self.network.nodes}
        edge_by_id = {edge.edge_id: edge for edge in self.network.edges}
        vehicle_ids = [arrival.vehicle.vehicle_id for arrival in self.arrivals]
        if len(vehicle_ids) != len(set(vehicle_ids)):
            raise ValueError("scheduled vehicle identifiers must be unique")

        for arrival in self.arrivals:
            vehicle = arrival.vehicle
            route = vehicle.route
            if vehicle.origin not in node_ids or vehicle.destination not in node_ids:
                raise ValueError("vehicle endpoints must exist in the simulation network")
            if route is None:
                raise ValueError("scheduled vehicles require a route")
            if route.node_ids[0] != vehicle.origin or route.node_ids[-1] != vehicle.destination:
                raise ValueError("vehicle route endpoints must match the vehicle")
            if len(route.edge_ids) != max(len(route.node_ids) - 1, 0):
                raise ValueError("simulation routes require explicit edge identities")
            for index, edge_id in enumerate(route.edge_ids):
                edge = edge_by_id.get(edge_id)
                if edge is None:
                    raise ValueError("vehicle routes must reference simulation network edges")
                if edge.source != route.node_ids[index] or edge.target != route.node_ids[index + 1]:
                    raise ValueError("vehicle route edge direction must match its node sequence")
        return self


class SimulationCounts(DomainModel):
    pending: int = Field(ge=0)
    active: int = Field(ge=0)
    completed: int = Field(ge=0)
    waiting: int = Field(ge=0)
    throughput: int = Field(ge=0)


class SimulationState(DomainModel):
    """Safely replaceable, JSON-compatible snapshot of simulation state."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    simulation_time_seconds: float = Field(ge=0.0)
    pending_vehicles: tuple[Vehicle, ...] = ()
    active_vehicles: tuple[Vehicle, ...] = ()
    completed_vehicles: tuple[Vehicle, ...] = ()
    waiting_vehicle_ids: tuple[Identifier, ...] = ()
    edge_occupancy: dict[Identifier, tuple[Identifier, ...]] = Field(default_factory=dict)
    edge_queues: dict[Identifier, tuple[Identifier, ...]] = Field(default_factory=dict)
    intersection_approach_queues: dict[Identifier, tuple[Identifier, ...]] = Field(
        default_factory=dict
    )
    counts: SimulationCounts

    @model_validator(mode="after")
    def validate_counts(self) -> Self:
        waiting = sum(
            vehicle.state is VehicleState.WAITING for vehicle in self.active_vehicles
        )
        expected = SimulationCounts(
            pending=len(self.pending_vehicles),
            active=len(self.active_vehicles),
            completed=len(self.completed_vehicles),
            waiting=waiting,
            throughput=len(self.completed_vehicles),
        )
        if self.counts != expected:
            raise ValueError("simulation aggregate counts do not match vehicle state")
        return self
