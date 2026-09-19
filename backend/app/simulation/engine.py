"""Deterministic discrete-time traffic simulation engine."""

from collections import defaultdict
from math import floor

from app.core.errors import SimulationError
from app.domain.network import NetworkEdge
from app.domain.vehicle import Vehicle, VehicleState
from app.simulation.models import SimulationScenario, SimulationState
from app.simulation.state import build_simulation_state
from app.simulation.vehicle import IntersectionEntryPolicy, PermitAllIntersections

_EPSILON = 1e-9


class TrafficSimulation:
    """Advance routed vehicles through capacity-constrained directed edges."""

    def __init__(
        self,
        scenario: SimulationScenario,
        *,
        entry_policy: IntersectionEntryPolicy | None = None,
    ) -> None:
        self._scenario = scenario
        self._entry_policy = entry_policy or PermitAllIntersections()
        self._edge_by_id = {edge.edge_id: edge for edge in scenario.network.edges}
        self._state = self._initial_state()

    @property
    def scenario(self) -> SimulationScenario:
        return self._scenario

    @property
    def state(self) -> SimulationState:
        return self._state

    def reset(self, scenario: SimulationScenario | None = None) -> SimulationState:
        """Reset to a deterministic time-zero snapshot."""
        if scenario is not None:
            self._scenario = scenario
            self._edge_by_id = {edge.edge_id: edge for edge in scenario.network.edges}
        self._state = self._initial_state()
        return self._state

    def step(self, seconds: float | None = None) -> SimulationState:
        """Advance one timestep, or a smaller explicit positive interval."""
        timestep = (
            self._scenario.configuration.timestep_seconds if seconds is None else seconds
        )
        if timestep <= 0:
            raise SimulationError("simulation step must be positive")
        current_time = self._state.simulation_time_seconds
        if current_time >= self._scenario.duration_seconds:
            return self._state
        next_time = min(current_time + timestep, self._scenario.duration_seconds)
        elapsed = next_time - current_time

        due, pending = self._partition_due_arrivals(next_time)
        active = list(self._state.active_vehicles)
        active.extend(self._spawn_vehicle(vehicle) for vehicle in due)
        occupancy = self._mutable_occupancy(self._state)
        completed = list(self._state.completed_vehicles)
        next_active: list[Vehicle] = []

        for vehicle in sorted(active, key=lambda item: item.vehicle_id):
            available_seconds = elapsed
            if vehicle.arrival_time_seconds > current_time:
                available_seconds = max(0.0, next_time - vehicle.arrival_time_seconds)
            advanced = self._advance_vehicle(
                vehicle,
                available_seconds,
                next_time,
                occupancy,
            )
            if advanced.state is VehicleState.ARRIVED:
                completed.append(advanced)
            else:
                next_active.append(advanced)

        self._state = build_simulation_state(
            simulation_time_seconds=next_time,
            network=self._scenario.network,
            pending_vehicles=tuple(pending),
            active_vehicles=tuple(next_active),
            completed_vehicles=tuple(completed),
        )
        return self._state

    def run(self, duration_seconds: float | None = None) -> SimulationState:
        """Advance for a bounded duration or to the scenario horizon."""
        if duration_seconds is not None and duration_seconds < 0:
            raise SimulationError("simulation run duration cannot be negative")
        target_time = self._scenario.duration_seconds
        if duration_seconds is not None:
            target_time = min(
                self._state.simulation_time_seconds + duration_seconds,
                self._scenario.duration_seconds,
            )
        while self._state.simulation_time_seconds + _EPSILON < target_time:
            remaining = target_time - self._state.simulation_time_seconds
            self.step(min(self._scenario.configuration.timestep_seconds, remaining))
        return self._state

    def _initial_state(self) -> SimulationState:
        due: list[Vehicle] = []
        pending: list[Vehicle] = []
        for arrival in sorted(
            self._scenario.arrivals,
            key=lambda item: (item.arrival_time_seconds, item.vehicle.vehicle_id),
        ):
            target = due if arrival.arrival_time_seconds <= 0 else pending
            target.append(arrival.vehicle.model_copy(deep=True))

        occupancy: dict[str, list[str]] = defaultdict(list)
        active: list[Vehicle] = []
        completed: list[Vehicle] = []
        placeholder = build_simulation_state(
            simulation_time_seconds=0.0,
            network=self._scenario.network,
            pending_vehicles=tuple(pending),
            active_vehicles=(),
            completed_vehicles=(),
        )
        for vehicle in due:
            spawned = self._spawn_vehicle(vehicle)
            entered = self._enter_initial_edge(spawned, occupancy, placeholder)
            if entered.state is VehicleState.ARRIVED:
                completed.append(entered)
            else:
                active.append(entered)
        return build_simulation_state(
            simulation_time_seconds=0.0,
            network=self._scenario.network,
            pending_vehicles=tuple(pending),
            active_vehicles=tuple(active),
            completed_vehicles=tuple(completed),
        )

    def _partition_due_arrivals(self, next_time: float) -> tuple[list[Vehicle], list[Vehicle]]:
        due: list[Vehicle] = []
        pending: list[Vehicle] = []
        for vehicle in self._state.pending_vehicles:
            target = due if vehicle.arrival_time_seconds <= next_time else pending
            target.append(vehicle)
        return due, pending

    def _spawn_vehicle(self, vehicle: Vehicle) -> Vehicle:
        return vehicle.model_copy(
            deep=True,
            update={
                "state": VehicleState.ACTIVE,
                "current_node_id": vehicle.origin,
                "current_edge_id": None,
                "current_route_index": 0,
                "position_on_edge": 0.0,
                "speed_kph": 0.0,
                "completion_time_seconds": None,
            },
        )

    def _advance_vehicle(
        self,
        vehicle: Vehicle,
        elapsed: float,
        next_time: float,
        occupancy: dict[str, list[str]],
    ) -> Vehicle:
        if elapsed <= _EPSILON:
            return self._enter_initial_edge(vehicle, occupancy, self._state)
        route = vehicle.route
        if route is None:
            raise SimulationError(f"vehicle {vehicle.vehicle_id} has no route")
        if not route.edge_ids:
            return self._complete_vehicle(vehicle, next_time, occupancy)

        current = vehicle
        if current.current_edge_id is None:
            current = self._enter_initial_edge(current, occupancy, self._state)
            if current.state is VehicleState.WAITING:
                return self._wait_vehicle(current, elapsed)

        remaining_seconds = elapsed
        while remaining_seconds > _EPSILON:
            current_edge = self._edge(current.current_edge_id)
            speed_mps = current_edge.free_flow_speed_kph / 3.6
            remaining_distance = current_edge.length_m * (1.0 - current.position_on_edge)
            seconds_to_end = remaining_distance / speed_mps
            if seconds_to_end > remaining_seconds + _EPSILON:
                travelled = speed_mps * remaining_seconds
                return current.model_copy(
                    update={
                        "state": VehicleState.ACTIVE,
                        "current_node_id": None,
                        "position_on_edge": min(
                            1.0,
                            current.position_on_edge + travelled / current_edge.length_m,
                        ),
                        "speed_kph": current_edge.free_flow_speed_kph,
                        "distance_travelled_m": current.distance_travelled_m + travelled,
                        "total_travel_time_seconds": (
                            current.total_travel_time_seconds + remaining_seconds
                        ),
                    }
                )

            current = current.model_copy(
                update={
                    "position_on_edge": 1.0,
                    "current_node_id": current_edge.target,
                    "distance_travelled_m": (
                        current.distance_travelled_m + remaining_distance
                    ),
                    "total_travel_time_seconds": (
                        current.total_travel_time_seconds + seconds_to_end
                    ),
                }
            )
            remaining_seconds = max(0.0, remaining_seconds - seconds_to_end)
            next_index = current.current_route_index + 1
            if next_index >= len(route.edge_ids):
                return self._complete_vehicle(current, next_time, occupancy)

            next_edge = self._edge(route.edge_ids[next_index])
            crossing_time = next_time - remaining_seconds
            if not self._can_enter(
                current,
                next_edge,
                occupancy,
                self._state,
                crossing_time,
            ):
                return self._wait_vehicle(current, remaining_seconds)
            self._leave_edge(current.current_edge_id, current.vehicle_id, occupancy)
            occupancy[next_edge.edge_id].append(current.vehicle_id)
            current = current.model_copy(
                update={
                    "state": VehicleState.ACTIVE,
                    "current_route_index": next_index,
                    "current_edge_id": next_edge.edge_id,
                    "current_node_id": None,
                    "position_on_edge": 0.0,
                    "speed_kph": next_edge.free_flow_speed_kph,
                }
            )
        return current

    def _enter_initial_edge(
        self,
        vehicle: Vehicle,
        occupancy: dict[str, list[str]],
        state: SimulationState,
    ) -> Vehicle:
        route = vehicle.route
        if route is None:
            raise SimulationError(f"vehicle {vehicle.vehicle_id} has no route")
        if not route.edge_ids:
            return self._complete_vehicle(vehicle, state.simulation_time_seconds, occupancy)
        if vehicle.current_edge_id is not None:
            return vehicle
        edge = self._edge(route.edge_ids[0])
        if not self._can_enter(
            vehicle,
            edge,
            occupancy,
            state,
            state.simulation_time_seconds,
        ):
            return vehicle.model_copy(
                update={"state": VehicleState.WAITING, "speed_kph": 0.0}
            )
        occupancy[edge.edge_id].append(vehicle.vehicle_id)
        return vehicle.model_copy(
            update={
                "state": VehicleState.ACTIVE,
                "current_route_index": 0,
                "current_edge_id": edge.edge_id,
                "current_node_id": None,
                "position_on_edge": 0.0,
                "speed_kph": edge.free_flow_speed_kph,
            }
        )

    def _can_enter(
        self,
        vehicle: Vehicle,
        edge: NetworkEdge,
        occupancy: dict[str, list[str]],
        state: SimulationState,
        at_time_seconds: float,
    ) -> bool:
        capacity = max(1, floor(edge.capacity))
        return (
            not edge.closed
            and len(occupancy[edge.edge_id]) < capacity
            and self._entry_policy.can_enter_next_edge(
                vehicle,
                edge,
                state,
                at_time_seconds,
            )
        )

    def _wait_vehicle(self, vehicle: Vehicle, seconds: float) -> Vehicle:
        return vehicle.model_copy(
            update={
                "state": VehicleState.WAITING,
                "speed_kph": 0.0,
                "waiting_time_seconds": vehicle.waiting_time_seconds + seconds,
                "stopped_time_seconds": vehicle.stopped_time_seconds + seconds,
                "total_travel_time_seconds": vehicle.total_travel_time_seconds + seconds,
            }
        )

    def _complete_vehicle(
        self,
        vehicle: Vehicle,
        completion_time: float,
        occupancy: dict[str, list[str]],
    ) -> Vehicle:
        self._leave_edge(vehicle.current_edge_id, vehicle.vehicle_id, occupancy)
        return vehicle.model_copy(
            update={
                "state": VehicleState.ARRIVED,
                "current_node_id": vehicle.destination,
                "current_edge_id": None,
                "position_on_edge": 0.0,
                "speed_kph": 0.0,
                "completion_time_seconds": completion_time,
            }
        )

    def _edge(self, edge_id: str | None) -> NetworkEdge:
        if edge_id is None or edge_id not in self._edge_by_id:
            raise SimulationError(f"unknown simulation edge: {edge_id}")
        return self._edge_by_id[edge_id]

    @staticmethod
    def _leave_edge(
        edge_id: str | None,
        vehicle_id: str,
        occupancy: dict[str, list[str]],
    ) -> None:
        if edge_id is not None and vehicle_id in occupancy[edge_id]:
            occupancy[edge_id].remove(vehicle_id)

    @staticmethod
    def _mutable_occupancy(state: SimulationState) -> dict[str, list[str]]:
        return defaultdict(
            list,
            {edge_id: list(vehicle_ids) for edge_id, vehicle_ids in state.edge_occupancy.items()},
        )
