"""Unit tests for traffic, queue, emergency, and scenario metrics."""

import pytest
from app.domain.metrics import EmergencyMetrics
from app.domain.vehicle import EmergencySubtype, Vehicle, VehicleState, VehicleType
from app.metrics.aggregation import emergency_metrics
from app.metrics.service import MetricsService
from app.metrics.traffic import calculate_traffic_metrics
from app.simulation.models import SimulationCounts, SimulationState


def test_basic_traffic_waiting_and_travel_metrics() -> None:
    completed = _vehicle(
        "completed",
        completed_at=60.0,
        waiting=10.0,
        total_travel=60.0,
    )
    active = _vehicle("active", waiting=20.0, total_travel=30.0)
    state = _state(120.0, active=(active,), completed=(completed,))

    metrics = calculate_traffic_metrics(state)

    assert metrics.total_vehicles == 2
    assert metrics.completed_vehicles == 1
    assert metrics.active_vehicles == 1
    assert metrics.completion_rate == 0.5
    assert metrics.throughput == 1
    assert metrics.throughput_per_minute == 0.5
    assert metrics.total_waiting_seconds == 30.0
    assert metrics.average_waiting_seconds == 15.0
    assert metrics.max_waiting_seconds == 20.0
    assert metrics.average_travel_seconds == 60.0
    assert metrics.max_travel_seconds == 60.0


def test_queue_metrics_use_real_trajectory_observations() -> None:
    waiting_one = _vehicle("waiting-1", waiting=1.0, state=VehicleState.WAITING)
    waiting_two = _vehicle("waiting-2", waiting=1.0, state=VehicleState.WAITING)
    first = _state(
        1.0,
        active=(waiting_one, waiting_two),
        waiting_ids=("waiting-1", "waiting-2"),
    )
    second = _state(
        2.0,
        active=(waiting_one,),
        waiting_ids=("waiting-1",),
    )
    final = _state(3.0)

    metrics = calculate_traffic_metrics(
        final,
        observations=(first, second, final),
    )

    assert metrics.max_queue_length == 2
    assert metrics.final_queue_length == 0
    assert metrics.average_queue_length == 1.0


def test_final_edge_and_intersection_approach_breakdowns() -> None:
    waiting = _vehicle("waiting-1", waiting=1.0, state=VehicleState.WAITING)

    metrics = calculate_traffic_metrics(
        _state(1.0, active=(waiting,), waiting_ids=("waiting-1",))
    )

    assert metrics.edges[0].edge_id == "E1"
    assert metrics.edges[0].occupancy == 1
    assert metrics.edges[0].queue_length == 1
    assert metrics.edges[0].waiting_vehicle_ids == ("waiting-1",)
    assert metrics.intersection_approaches[0].approach_id == "E1"
    assert metrics.intersection_approaches[0].queue_length == 1


def test_per_vehicle_metrics_exclude_incomplete_travel_time() -> None:
    completed = _vehicle("completed", completed_at=25.0, waiting=5.0)
    active = _vehicle("active", waiting=3.0)

    metrics = calculate_traffic_metrics(
        _state(30.0, active=(active,), completed=(completed,))
    )
    results = {result.vehicle_id: result for result in metrics.per_vehicle}

    assert results["completed"].completed is True
    assert results["completed"].travel_time_seconds == 25.0
    assert results["active"].completed is False
    assert results["active"].travel_time_seconds is None


def test_emergency_metrics_measure_completed_and_active_vehicles() -> None:
    completed = _vehicle(
        "emergency-completed",
        completed_at=60.0,
        waiting=10.0,
        emergency=True,
    )
    active = _vehicle("emergency-active", waiting=20.0, emergency=True)

    metrics = emergency_metrics((active, completed))

    assert metrics == EmergencyMetrics(
        emergency_total=2,
        emergency_completed=1,
        emergency_active=1,
        emergency_completion_rate=0.5,
        emergency_total_waiting_seconds=30.0,
        emergency_average_waiting_seconds=15.0,
        emergency_average_travel_seconds=60.0,
    )


def test_zero_vehicle_and_zero_duration_metrics_are_safe() -> None:
    metrics = MetricsService().evaluate("empty", _state(0.0))

    assert metrics.traffic_metrics.completion_rate == 0.0
    assert metrics.traffic_metrics.throughput_per_minute == 0.0
    assert metrics.traffic_metrics.average_waiting_seconds == 0.0
    assert metrics.traffic_metrics.average_travel_seconds == 0.0
    assert metrics.environmental_metrics.fuel_liters == 0.0
    assert metrics.environmental_metrics.co2_kg == 0.0
    assert metrics.emergency_metrics.emergency_completion_rate == 0.0


def test_scenario_result_is_json_serializable() -> None:
    completed = _vehicle("completed", completed_at=10.0, total_travel=10.0)

    result = MetricsService().evaluate(
        "scenario-1",
        _state(10.0, completed=(completed,)),
    )
    payload = result.model_dump(mode="json")

    assert payload["scenario_id"] == "scenario-1"
    assert payload["traffic_metrics"]["completion_rate"] == 1.0
    assert payload["environmental_metrics"]["is_estimate"] is True


def test_invalid_traffic_count_relationship_is_rejected() -> None:
    completed = _vehicle("completed", completed_at=10.0)
    metrics = calculate_traffic_metrics(_state(10.0, completed=(completed,)))

    with pytest.raises(ValueError, match="total vehicles"):
        metrics.model_copy(update={"total_vehicles": 2}).model_validate(
            metrics.model_copy(update={"total_vehicles": 2}).model_dump()
        )


def _vehicle(
    vehicle_id: str,
    *,
    completed_at: float | None = None,
    waiting: float = 0.0,
    total_travel: float = 0.0,
    state: VehicleState = VehicleState.ACTIVE,
    emergency: bool = False,
) -> Vehicle:
    completed = completed_at is not None
    return Vehicle(
        vehicle_id=vehicle_id,
        vehicle_type=VehicleType.EMERGENCY if emergency else VehicleType.REGULAR,
        origin="I1",
        destination="I2",
        is_emergency=emergency,
        emergency_subtype=EmergencySubtype.AMBULANCE if emergency else None,
        priority_weight=10 if emergency else 1,
        state=VehicleState.ARRIVED if completed else state,
        arrival_time_seconds=0.0,
        completion_time_seconds=completed_at,
        total_travel_time_seconds=total_travel,
        waiting_time_seconds=waiting,
        stopped_time_seconds=waiting,
    )


def _state(
    time_seconds: float,
    *,
    active: tuple[Vehicle, ...] = (),
    completed: tuple[Vehicle, ...] = (),
    waiting_ids: tuple[str, ...] = (),
) -> SimulationState:
    return SimulationState(
        simulation_time_seconds=time_seconds,
        active_vehicles=active,
        completed_vehicles=completed,
        waiting_vehicle_ids=waiting_ids,
        edge_occupancy={"E1": tuple(vehicle.vehicle_id for vehicle in active)},
        edge_queues={"E1": waiting_ids},
        intersection_approach_queues={"E1": waiting_ids} if waiting_ids else {},
        counts=SimulationCounts(
            pending=0,
            active=len(active),
            completed=len(completed),
            waiting=len(waiting_ids),
            throughput=len(completed),
        ),
    )
