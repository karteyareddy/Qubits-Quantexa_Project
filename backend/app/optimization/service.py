"""Public optimization service consuming network contracts and candidate routes."""

from collections.abc import Sequence
from dataclasses import dataclass, field

from app.domain.network import Network
from app.domain.optimization import OptimizationResult
from app.domain.vehicle import Vehicle
from app.optimization.objective import PriorityMTFConfig
from app.optimization.priority_mtf import run_priority_aware_mtf


@dataclass(frozen=True)
class PriorityMTFOptimizerService:
    config: PriorityMTFConfig = field(default_factory=PriorityMTFConfig)

    def optimize(
        self,
        optimization_id: str,
        network: Network,
        vehicles: Sequence[Vehicle],
        candidate_routes_map: dict[str, Sequence[tuple[str, ...]]],
        *,
        method: str = "neal",
        num_reads: int = 200,
    ) -> OptimizationResult:
        """Execute Priority-Aware MTF optimization on domain network and vehicles."""
        edge_base_times: dict[tuple[str, str], float] = {
            (edge.source, edge.target): edge.travel_time_seconds
            for edge in network.edges
        }

        return run_priority_aware_mtf(
            optimization_id,
            vehicles,
            candidate_routes_map,
            edge_base_times,
            config=self.config,
            method=method,
            num_reads=num_reads,
        )
