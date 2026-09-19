"""Unit tests for API request and response Pydantic schemas."""

from app.api.schemas.events import (
    AccidentEventRequest,
    CongestionSpikeEventRequest,
    EmergencyArrivalEventRequest,
    RoadClosureEventRequest,
)
from app.api.schemas.network import NetworkSchema
from app.api.schemas.optimization import OptimizationRequest
from app.api.schemas.simulation import SimulationCreateRequest, SimulationStepRequest


def test_simulation_create_request_defaults() -> None:
    req = SimulationCreateRequest()
    assert req.scenario_id == "low-traffic"
    assert req.control_interval_seconds == 5.0
    assert req.seed == 42
    assert req.adaptive_enabled is True
    assert req.events_enabled is True
    assert req.emergency_corridor_enabled is True


def test_simulation_step_request() -> None:
    req = SimulationStepRequest(step_seconds=2.5)
    assert req.step_seconds == 2.5


def test_optimization_request_defaults() -> None:
    req = OptimizationRequest()
    assert req.solver == "hybrid"
    assert req.apply_immediately is True


def test_event_discriminated_schemas() -> None:
    cs = CongestionSpikeEventRequest(type="congestion_spike", timestamp=10.0, edge_id="I1->I2", multiplier=3.0)
    assert cs.type == "congestion_spike"
    assert cs.multiplier == 3.0

    acc = AccidentEventRequest(type="accident", timestamp=15.0, edge_id="I2->I5", capacity_reduction=0.4)
    assert acc.type == "accident"
    assert acc.capacity_reduction == 0.4

    rc = RoadClosureEventRequest(type="road_closure", timestamp=20.0, target="I1->I4", duration=40.0)
    assert rc.type == "road_closure"

    ea = EmergencyArrivalEventRequest(type="emergency_arrival", timestamp=25.0, vehicle_id="amb-01", origin="I1", destination="I6")
    assert ea.type == "emergency_arrival"
    assert ea.emergency_subtype == "AMBULANCE"


def test_network_schema_construction() -> None:
    net = NetworkSchema(intersections=[], edges=[], signalized_intersections=["I1", "I2"])
    assert len(net.signalized_intersections) == 2
