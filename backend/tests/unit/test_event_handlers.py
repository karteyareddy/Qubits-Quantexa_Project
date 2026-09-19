"""Unit tests for event handlers and event engine."""

import pytest
from app.domain.vehicle import VehicleType
from app.events.engine import EventEngine
from app.events.handlers import apply_event, restore_event_effect
from app.events.models import (
    AccidentEvent,
    CongestionSpikeEvent,
    EmergencyArrivalEvent,
    EventStatus,
    RoadClosureEvent,
)
from app.events.scheduler import EventScheduler
from app.simulation.engine import TrafficSimulation
from app.simulation.scenarios import low_traffic_scenario


@pytest.fixture
def sim() -> TrafficSimulation:
    scenario = low_traffic_scenario()
    return TrafficSimulation(scenario)


def test_accident_handler_apply_and_restore(sim: TrafficSimulation) -> None:
    active_effects: dict = {}
    event = AccidentEvent(
        event_id="acc1",
        timestamp=10.0,
        target="I1->I2",
        capacity_factor=0.25,
        duration=20.0,
    )

    edge_map = {e.edge_id: e for e in sim.scenario.network.edges}
    orig_cap = edge_map["I1->I2"].capacity

    rec = apply_event(event, sim, active_effects)
    assert rec.status == EventStatus.ACTIVE
    assert edge_map["I1->I2"].capacity == max(1.0, orig_cap * 0.25)
    assert "acc1" in active_effects

    restore_event_effect("acc1", sim, active_effects)
    assert edge_map["I1->I2"].capacity == orig_cap
    assert "acc1" not in active_effects


def test_road_closure_handler_apply_and_restore(sim: TrafficSimulation) -> None:
    active_effects: dict = {}
    event = RoadClosureEvent(
        event_id="rc1",
        timestamp=15.0,
        target="I2->I5",
        duration=30.0,
    )

    edge_map = {e.edge_id: e for e in sim.scenario.network.edges}
    assert not edge_map["I2->I5"].closed

    rec = apply_event(event, sim, active_effects)
    assert rec.status == EventStatus.ACTIVE
    assert edge_map["I2->I5"].closed
    assert "rc1" in active_effects

    restore_event_effect("rc1", sim, active_effects)
    assert not edge_map["I2->I5"].closed
    assert "rc1" not in active_effects


def test_congestion_spike_handler(sim: TrafficSimulation) -> None:
    active_effects: dict = {}
    initial_pending = len(sim.state.pending_vehicles)

    event = CongestionSpikeEvent(
        event_id="cs1",
        timestamp=5.0,
        target="I1->I2",
        additional_vehicle_count=4,
    )

    rec = apply_event(event, sim, active_effects)
    assert rec.status == EventStatus.RESOLVED
    assert len(sim.state.pending_vehicles) == initial_pending + 4
    added = [v for v in sim.state.pending_vehicles if v.vehicle_id.startswith("congestion_cs1_")]
    assert len(added) == 4


def test_emergency_arrival_handler(sim: TrafficSimulation) -> None:
    active_effects: dict = {}
    initial_pending = len(sim.state.pending_vehicles)

    event = EmergencyArrivalEvent(
        event_id="em1",
        timestamp=10.0,
        target="I1",
        vehicle_id="amb_999",
        origin="I1",
        destination="I6",
        priority=10,
    )

    rec = apply_event(event, sim, active_effects)
    assert rec.status == EventStatus.RESOLVED
    assert len(sim.state.pending_vehicles) == initial_pending + 1
    em_vehs = [v for v in sim.state.pending_vehicles if v.vehicle_id == "amb_999"]
    assert len(em_vehs) == 1
    em_veh = em_vehs[0]
    assert em_veh.is_emergency
    assert em_veh.vehicle_type == VehicleType.EMERGENCY
    assert em_veh.priority_weight == 10


def test_event_engine_lifecycle(sim: TrafficSimulation) -> None:
    scheduler = EventScheduler()
    acc = AccidentEvent(
        event_id="acc1",
        timestamp=5.0,
        target="I1->I2",
        capacity_factor=0.5,
        duration=10.0,
    )
    scheduler.add_event(acc)

    engine = EventEngine(scheduler=scheduler)

    # t=0: no events due
    applied = engine.process_due_events(sim)
    assert len(applied) == 0

    # Advance simulation to t=5.0
    sim.step(5.0)
    applied = engine.process_due_events(sim)
    assert len(applied) == 1
    assert applied[0].event_id == "acc1"
    assert engine.get_event_metrics()["active_event_count"] == 1

    # Advance simulation to t=15.0 (event expired)
    sim.step(10.0)
    expired = engine.check_expirations(sim)
    assert len(expired) == 1
    assert expired[0].event_id == "acc1"
    assert expired[0].status == EventStatus.EXPIRED
    assert engine.get_event_metrics()["active_event_count"] == 0
