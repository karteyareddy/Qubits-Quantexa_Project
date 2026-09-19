"""Integration tests for Stage 12 dynamic traffic event execution."""

from app.adaptive.config import AdaptiveConfig
from app.events.models import (
    AccidentEvent,
    CongestionSpikeEvent,
    EmergencyArrivalEvent,
    EventStatus,
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


def test_scenario_a_congestion_spike() -> None:
    scenario = low_traffic_scenario()
    runner = DynamicSimulationRunner(
        adaptive_config=_build_test_adaptive_config()
    )

    spike = CongestionSpikeEvent(
        event_id="cs_test",
        timestamp=10.0,
        target="I1->I2",
        additional_vehicle_count=5,
    )

    res = runner.run_dynamic_simulation(scenario=scenario, events=[spike], duration_seconds=30.0)

    assert len(res.event_history) == 1
    assert res.event_history[0].event_id == "cs_test"
    assert res.event_history[0].status == EventStatus.RESOLVED

    # Check optimization ran and observed updated state
    assert len(res.adaptive_result.optimization_events) >= 3


def test_scenario_b_accident_lifecycle() -> None:
    scenario = low_traffic_scenario()
    runner = DynamicSimulationRunner(
        adaptive_config=_build_test_adaptive_config()
    )

    acc = AccidentEvent(
        event_id="acc_test",
        timestamp=10.0,
        target="I2->I5",
        severity=0.7,
        capacity_factor=0.25,
        duration=15.0,
    )

    res = runner.run_dynamic_simulation(scenario=scenario, events=[acc], duration_seconds=30.0)

    history = {r.event_id: r for r in res.event_history}
    assert "acc_test" in history
    assert history["acc_test"].status == EventStatus.EXPIRED

    # Check capacity restored on original scenario network edge
    edge_map = {e.edge_id: e for e in scenario.network.edges}
    assert edge_map["I2->I5"].capacity == 18.0


def test_scenario_c_road_closure_lifecycle() -> None:
    scenario = low_traffic_scenario()
    runner = DynamicSimulationRunner(
        adaptive_config=_build_test_adaptive_config()
    )

    closure = RoadClosureEvent(
        event_id="rc_test",
        timestamp=10.0,
        target="I1->I4",
        duration=15.0,
    )

    res = runner.run_dynamic_simulation(scenario=scenario, events=[closure], duration_seconds=30.0)

    history = {r.event_id: r for r in res.event_history}
    assert "rc_test" in history
    assert history["rc_test"].status == EventStatus.EXPIRED

    # Edge closed during t=10..25 and reopened after t=25
    edge_map = {e.edge_id: e for e in scenario.network.edges}
    assert not edge_map["I1->I4"].closed


def test_scenario_d_emergency_arrival() -> None:
    scenario = low_traffic_scenario()
    runner = DynamicSimulationRunner(
        adaptive_config=_build_test_adaptive_config()
    )

    em = EmergencyArrivalEvent(
        event_id="em_test",
        timestamp=10.0,
        target="I1",
        vehicle_id="amb_01",
        origin="I1",
        destination="I6",
        priority=10,
    )

    res = runner.run_dynamic_simulation(scenario=scenario, events=[em], duration_seconds=30.0)

    history = {r.event_id: r for r in res.event_history}
    assert "em_test" in history

    # Verify metrics detected emergency vehicle
    em_metrics = res.adaptive_result.metrics.emergency_metrics
    assert em_metrics.emergency_total >= 1


def test_combined_multi_event_scenario() -> None:
    scenario = low_traffic_scenario()
    runner = DynamicSimulationRunner(
        adaptive_config=_build_test_adaptive_config()
    )

    events = [
        CongestionSpikeEvent(
            event_id="cs1",
            timestamp=5.0,
            target="I1->I2",
            additional_vehicle_count=3,
        ),
        AccidentEvent(
            event_id="acc1",
            timestamp=10.0,
            target="I2->I5",
            capacity_factor=0.3,
            duration=10.0,
        ),
        EmergencyArrivalEvent(
            event_id="em1",
            timestamp=15.0,
            target="I1",
            vehicle_id="amb_combined",
            origin="I1",
            destination="I6",
            priority=10,
        ),
        RoadClosureEvent(
            event_id="rc1",
            timestamp=20.0,
            target="I4->I5",
            duration=10.0,
        ),
    ]

    res = runner.run_dynamic_simulation(scenario=scenario, events=events, duration_seconds=35.0)

    assert len(res.event_history) == 4
    for record in res.event_history:
        assert record.status in (EventStatus.RESOLVED, EventStatus.EXPIRED)

    # Verify adaptive closed-loop optimization completed cleanly
    assert len(res.adaptive_result.optimization_events) >= 3
    assert res.adaptive_result.duration_seconds == 35.0
