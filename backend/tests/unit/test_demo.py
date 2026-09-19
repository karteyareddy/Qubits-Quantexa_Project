"""Unit tests for Stage 19 demo subsystem."""

from app.demo import (
    DemoConfig,
    DemoRunner,
    build_demo_scenario,
)


def test_build_demo_scenario() -> None:
    scenario, events = build_demo_scenario(seed=42, duration_seconds=60.0)
    assert scenario.scenario_id == "demo-scenario"
    assert scenario.duration_seconds == 60.0
    assert len(events) == 2
    assert events[0].event_type.value == "congestion"
    assert events[1].event_type.value == "emergency_arrival"


def test_demo_runner_execution() -> None:
    config = DemoConfig(seed=42, duration_seconds=30.0, control_interval_seconds=10.0)
    runner = DemoRunner()
    result = runner.run_demo(config)

    assert result.status == "COMPLETED"
    assert result.duration_seconds == 30.0
    assert result.seed == 42
    assert result.total_vehicles_spawned > 0
    assert len(result.milestones) >= 4
    assert any(m.subsystem == "events" for m in result.milestones)
    assert any(m.subsystem == "optimization" for m in result.milestones)
