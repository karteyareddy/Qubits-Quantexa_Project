"""Integration tests for Stage 13 Emergency Green Corridor preemption & adaptive control."""

from app.adaptive.config import AdaptiveConfig
from app.emergency.models import CorridorStatus
from app.events.models import (
    AccidentEvent,
    CongestionSpikeEvent,
    EmergencyArrivalEvent,
    RoadClosureEvent,
)
from app.events.service import DynamicSimulationRunner
from app.optimization.hybrid_models import HybridOptimizerConfig
from app.quantum.config import QAOAConfig
from app.signals.qubo.config import SignalQuboConfig
from app.simulation.scenarios import low_traffic_scenario


def _build_test_adaptive_config() -> AdaptiveConfig:
    q_cfg = SignalQuboConfig(horizon_intervals=1)
    qaoa_cfg = QAOAConfig(reps=1, shots=256, seed=42, max_iterations=10)
    hybrid_cfg = HybridOptimizerConfig(
        mode="hybrid",
        candidate_count=5,
        enable_refinement=True,
        qubo_config=q_cfg,
        qaoa_config=qaoa_cfg,
    )
    return AdaptiveConfig(
        control_interval_seconds=10.0,
        enabled=True,
        hybrid_config=hybrid_cfg,
    )


def test_basic_emergency_corridor_simulation() -> None:
    scenario = low_traffic_scenario()
    runner = DynamicSimulationRunner(adaptive_config=_build_test_adaptive_config())

    em_event = EmergencyArrivalEvent(
        event_id="em_corridor_01",
        timestamp=10.0,
        target="I1",
        vehicle_id="amb_corridor_1",
        origin="I1",
        destination="I6",
        priority=20,
    )

    result = runner.run_dynamic_simulation(
        scenario=scenario,
        events=[em_event],
        duration_seconds=40.0,
        run_id="corridor-test-1",
    )

    history = runner.emergency_service.corridor_history
    assert len(history) == 1
    corridor = history[0]
    assert corridor.vehicle_id == "amb_corridor_1"
    assert corridor.status in (CorridorStatus.ACTIVE, CorridorStatus.COMPLETED)
    assert len(corridor.intersections) > 0

    # Verify emergency metrics tracked vehicle
    em_metrics = result.adaptive_result.metrics.emergency_metrics
    assert em_metrics.emergency_total >= 1


def test_non_emergency_traffic_conflict_protection() -> None:
    scenario = low_traffic_scenario()
    runner = DynamicSimulationRunner(adaptive_config=_build_test_adaptive_config())

    em_event = EmergencyArrivalEvent(
        event_id="em_corridor_02",
        timestamp=10.0,
        target="I1",
        vehicle_id="amb_corridor_2",
        origin="I1",
        destination="I6",
        priority=20,
    )

    result = runner.run_dynamic_simulation(
        scenario=scenario,
        events=[em_event],
        duration_seconds=30.0,
    )

    # Check signal states at each intersection remain valid
    for intersection_id, phase in result.adaptive_result.final_signal_state.items():
        assert phase is not None
        assert intersection_id in ("I1", "I2", "I3", "I4", "I5", "I6")


def test_road_closure_rerouting_interaction() -> None:
    scenario = low_traffic_scenario()
    runner = DynamicSimulationRunner(adaptive_config=_build_test_adaptive_config())

    events = [
        EmergencyArrivalEvent(
            event_id="em_reroute",
            timestamp=5.0,
            target="I1",
            vehicle_id="amb_reroute",
            origin="I1",
            destination="I6",
            priority=20,
        ),
        RoadClosureEvent(
            event_id="closure_reroute",
            timestamp=10.0,
            target="I1->I2",
            duration=15.0,
        ),
    ]

    result = runner.run_dynamic_simulation(
        scenario=scenario,
        events=events,
        duration_seconds=30.0,
    )

    assert len(result.event_history) == 2
    history = runner.emergency_service.corridor_history
    assert len(history) >= 1


def test_multiple_emergency_arrivals_policy() -> None:
    scenario = low_traffic_scenario()
    runner = DynamicSimulationRunner(adaptive_config=_build_test_adaptive_config())

    events = [
        EmergencyArrivalEvent(
            event_id="em_multi_1",
            timestamp=5.0,
            target="I1",
            vehicle_id="amb_m1",
            origin="I1",
            destination="I6",
            priority=20,
        ),
        EmergencyArrivalEvent(
            event_id="em_multi_2",
            timestamp=15.0,
            target="I4",
            vehicle_id="amb_m2",
            origin="I4",
            destination="I3",
            priority=20,
        ),
    ]

    result = runner.run_dynamic_simulation(
        scenario=scenario,
        events=events,
        duration_seconds=35.0,
    )

    history = runner.emergency_service.corridor_history
    assert len(history) == 2
    for c in history:
        assert c.status in (CorridorStatus.ACTIVE, CorridorStatus.COMPLETED)
    assert result.adaptive_result.duration_seconds == 35.0


def test_end_to_end_event_adaptive_corridor_pipeline() -> None:
    scenario = low_traffic_scenario()
    runner = DynamicSimulationRunner(adaptive_config=_build_test_adaptive_config())

    events = [
        CongestionSpikeEvent(
            event_id="cs_pipeline",
            timestamp=5.0,
            target="I1->I2",
            additional_vehicle_count=3,
        ),
        AccidentEvent(
            event_id="acc_pipeline",
            timestamp=10.0,
            target="I2->I5",
            capacity_factor=0.3,
            duration=10.0,
        ),
        EmergencyArrivalEvent(
            event_id="em_pipeline",
            timestamp=15.0,
            target="I1",
            vehicle_id="amb_pipeline",
            origin="I1",
            destination="I6",
            priority=20,
        ),
        RoadClosureEvent(
            event_id="rc_pipeline",
            timestamp=20.0,
            target="I4->I5",
            duration=10.0,
        ),
    ]

    result = runner.run_dynamic_simulation(
        scenario=scenario,
        events=events,
        duration_seconds=35.0,
    )

    assert len(result.event_history) == 4
    assert len(result.adaptive_result.optimization_events) >= 3

    corridor_history = runner.emergency_service.corridor_history
    assert len(corridor_history) >= 1
    assert result.adaptive_result.duration_seconds == 35.0
