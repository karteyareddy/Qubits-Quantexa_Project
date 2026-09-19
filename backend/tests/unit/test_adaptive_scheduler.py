"""Unit tests for AdaptiveScheduler optimization cadence."""

from app.adaptive.config import AdaptiveConfig
from app.adaptive.scheduler import AdaptiveScheduler


def test_adaptive_scheduler_boundary_checks() -> None:
    config = AdaptiveConfig(control_interval_seconds=10.0, enabled=True)
    scheduler = AdaptiveScheduler(config=config)

    # t = 0.0 -> boundary -> True
    assert scheduler.is_optimization_due(0.0) is True
    scheduler.mark_optimized(0.0)

    # t = 0.0 again -> duplicate -> False
    assert scheduler.is_optimization_due(0.0) is False

    # t = 5.0 -> non-boundary -> False
    assert scheduler.is_optimization_due(5.0) is False

    # t = 10.0 -> boundary -> True
    assert scheduler.is_optimization_due(10.0) is True
    scheduler.mark_optimized(10.0)

    assert scheduler.optimization_count == 2
