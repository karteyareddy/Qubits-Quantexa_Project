"""Integration tests for signal-controlled simulation transitions."""

from app.domain.network import Network, NetworkEdge, NetworkNode
from app.domain.route import Route
from app.domain.vehicle import Vehicle, VehicleState, VehicleType
from app.signals.models import SignalTiming
from app.signals.policy import FixedTimeSignalPolicy, SignalSystem
from app.simulation.engine import TrafficSimulation
from app.simulation.models import ScheduledArrival, SimulationScenario


def test_red_signal_stops_vehicle_and_increases_waiting_time() -> None:
    scenario = _turn_scenario()
    policy = _policy(scenario.network, green_seconds=1)
    simulation = TrafficSimulation(scenario, entry_policy=policy)

    simulation.step()
    state = simulation.step()
    vehicle = state.active_vehicles[0]

    assert vehicle.state is VehicleState.WAITING
    assert vehicle.current_edge_id == "I1->I2"
    assert vehicle.waiting_time_seconds == 1.0
    assert state.edge_queues["I2->I3"] == ("mover",)


def test_green_signal_allows_vehicle_to_cross_intersection() -> None:
    scenario = _turn_scenario()
    policy = _policy(scenario.network, green_seconds=2)
    simulation = TrafficSimulation(scenario, entry_policy=policy)

    state = simulation.step()
    vehicle = state.active_vehicles[0]

    assert vehicle.state is VehicleState.ACTIVE
    assert vehicle.current_edge_id == "I2->I3"
    assert vehicle.waiting_time_seconds == 0.0


def test_green_signal_does_not_override_downstream_capacity() -> None:
    scenario = _turn_scenario(include_blocker=True)
    policy = _policy(scenario.network, green_seconds=3)
    simulation = TrafficSimulation(scenario, entry_policy=policy)

    simulation.step()
    state = simulation.step()
    mover = next(
        vehicle for vehicle in state.active_vehicles if vehicle.vehicle_id == "mover"
    )

    assert mover.state is VehicleState.WAITING
    assert mover.waiting_time_seconds == 1.0
    assert state.edge_queues["I2->I3"] == ("mover",)


def test_vehicle_waits_then_crosses_and_completes() -> None:
    scenario = _turn_scenario()
    policy = _policy(scenario.network, green_seconds=1)
    simulation = TrafficSimulation(scenario, entry_policy=policy)

    state = simulation.run(6.0)
    vehicle = state.completed_vehicles[0]

    assert state.counts.completed == 1
    assert vehicle.waiting_time_seconds == 3.0
    assert vehicle.completion_time_seconds == 5.0


def _policy(network: Network, *, green_seconds: int) -> FixedTimeSignalPolicy:
    timing = SignalTiming(
        green_seconds=green_seconds,
        yellow_seconds=1,
        all_red_seconds=0,
    )
    return FixedTimeSignalPolicy(SignalSystem.for_network(network, timing=timing))


def _turn_scenario(*, include_blocker: bool = False) -> SimulationScenario:
    network = Network(
        network_id="signal-turn",
        directed=True,
        nodes=(
            NetworkNode(node_id="I1", x=0.0, y=0.0),
            NetworkNode(node_id="I2", x=1.0, y=0.0),
            NetworkNode(node_id="I3", x=1.0, y=1.0),
        ),
        edges=(
            NetworkEdge(
                edge_id="I1->I2",
                source="I1",
                target="I2",
                length_m=10.0,
                capacity=2.0,
                free_flow_speed_kph=36.0,
                travel_time_seconds=1.0,
            ),
            NetworkEdge(
                edge_id="I2->I3",
                source="I2",
                target="I3",
                length_m=10.0 if not include_blocker else 100.0,
                capacity=1.0,
                free_flow_speed_kph=36.0,
                travel_time_seconds=1.0 if not include_blocker else 10.0,
            ),
        ),
    )
    mover_route = Route(
        route_id="mover-route",
        node_ids=("I1", "I2", "I3"),
        edge_ids=("I1->I2", "I2->I3"),
        estimated_travel_time_seconds=2.0,
        distance_m=20.0,
    )
    arrivals = [
        ScheduledArrival(
            arrival_time_seconds=0.0,
            vehicle=Vehicle(
                vehicle_id="mover",
                vehicle_type=VehicleType.REGULAR,
                origin="I1",
                destination="I3",
                route=mover_route,
            ),
        )
    ]
    if include_blocker:
        blocker_route = Route(
            route_id="blocker-route",
            node_ids=("I2", "I3"),
            edge_ids=("I2->I3",),
            estimated_travel_time_seconds=10.0,
            distance_m=100.0,
        )
        arrivals.append(
            ScheduledArrival(
                arrival_time_seconds=0.0,
                vehicle=Vehicle(
                    vehicle_id="blocker",
                    vehicle_type=VehicleType.REGULAR,
                    origin="I2",
                    destination="I3",
                    route=blocker_route,
                ),
            )
        )
    return SimulationScenario(
        scenario_id="signal-turn-scenario",
        seed=42,
        duration_seconds=20.0,
        network=network,
        arrivals=tuple(arrivals),
    )
