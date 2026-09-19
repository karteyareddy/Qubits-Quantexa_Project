"""Typed domain contracts for Adaptive Traffic Optimization runs and events."""

from pydantic import Field

from app.domain.base import DomainModel
from app.domain.metrics import ScenarioMetrics
from app.domain.signal import SignalPhase
from app.domain.signal_qubo import SignalSchedule


class AdaptiveOptimizationEvent(DomainModel):
    """Record of a single optimization cycle executed during adaptive simulation."""

    timestamp: float = Field(ge=0.0, description="Simulation timestamp in seconds when optimization was triggered")
    interval_index: int = Field(ge=0, description="Index of control interval (0, 1, 2...)")
    status: str = Field(description="Optimization status ('success', 'fallback', 'failed', 'retained_previous')")
    solver_name: str = Field(description="Explicit solver identity ('qaoa', 'hybrid_qaoa', 'classical_reference')")
    qubo_energy: float = Field(description="Exact Stage 8 QUBO energy of selected signal schedule")
    is_feasible: bool = Field(description="Whether selected schedule satisfies signal phase constraints")
    schedule: SignalSchedule | None = Field(default=None, description="Decoded signal schedule applied")
    optimization_time: float = Field(ge=0.0, description="Wall-clock time in seconds spent in optimization")
    fallback_used: bool = Field(default=False, description="Whether classical fallback solver was used")
    fallback_reason: str | None = Field(default=None, description="Reason for fallback if applicable")


class AdaptiveRunResult(DomainModel):
    """Result data structure returned by AdaptiveSimulationRunner."""

    run_id: str = Field(description="Unique identifier for adaptive simulation run")
    duration_seconds: float = Field(gt=0.0, description="Total requested simulation duration")
    control_interval_seconds: float = Field(gt=0.0, description="Interval in seconds between optimizations")
    optimization_count: int = Field(ge=0, description="Total number of optimization cycles triggered")
    optimization_events: tuple[AdaptiveOptimizationEvent, ...] = Field(
        default_factory=tuple, description="Chronological record of optimization events"
    )
    final_simulation_time: float = Field(ge=0.0, description="Final simulation time achieved")
    final_signal_state: dict[str, SignalPhase] = Field(
        default_factory=dict, description="Active signal phases at final simulation time"
    )
    metrics: ScenarioMetrics = Field(description="Stage 6 scenario metrics summary")
    total_optimization_time: float = Field(ge=0.0, description="Cumulative time spent optimizing across all cycles")
    average_optimization_time: float = Field(ge=0.0, description="Average time per optimization cycle")
