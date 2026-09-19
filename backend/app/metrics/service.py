"""Public scenario metrics service independent from optimization."""

from collections.abc import Sequence
from dataclasses import dataclass, field

from app.domain.metrics import ScenarioMetrics
from app.metrics.aggregation import emergency_metrics, spawned_vehicles
from app.metrics.environmental import EnvironmentalConfig, estimate_environmental_metrics
from app.metrics.traffic import calculate_traffic_metrics
from app.simulation.models import SimulationState


@dataclass(frozen=True)
class MetricsService:
    environmental_config: EnvironmentalConfig = field(default_factory=EnvironmentalConfig)

    def evaluate(
        self,
        scenario_id: str,
        final_state: SimulationState,
        *,
        observations: Sequence[SimulationState] = (),
    ) -> ScenarioMetrics:
        vehicles = spawned_vehicles(final_state)
        return ScenarioMetrics(
            scenario_id=scenario_id,
            simulation_duration_seconds=final_state.simulation_time_seconds,
            traffic_metrics=calculate_traffic_metrics(
                final_state,
                observations=observations,
            ),
            environmental_metrics=estimate_environmental_metrics(
                vehicles,
                config=self.environmental_config,
            ),
            emergency_metrics=emergency_metrics(vehicles),
        )
