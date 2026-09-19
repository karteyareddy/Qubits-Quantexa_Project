"""AdaptiveScheduler managing optimization trigger cadence."""

from app.adaptive.config import AdaptiveConfig


class AdaptiveScheduler:
    """Tracks simulation time and determines when optimization cycles should trigger."""

    def __init__(self, config: AdaptiveConfig | None = None) -> None:
        self.config = config or AdaptiveConfig()
        self.last_optimization_time: float | None = None
        self.optimization_count: int = 0

    def is_optimization_due(self, simulation_time: float) -> bool:
        """Return True if an optimization cycle is due at simulation_time."""
        if not self.config.enabled:
            return False

        # Do not optimize twice at the exact same timestamp
        if self.last_optimization_time is not None and abs(simulation_time - self.last_optimization_time) < 1e-6:
            return False

        interval = self.config.control_interval_seconds
        # Check if simulation_time is at an exact control boundary (t = 0, 10, 20...)
        remainder = simulation_time % interval
        is_boundary = abs(remainder) < 1e-6 or abs(remainder - interval) < 1e-6

        return is_boundary

    def mark_optimized(self, simulation_time: float) -> None:
        """Record that optimization was successfully executed at simulation_time."""
        self.last_optimization_time = simulation_time
        self.optimization_count += 1
