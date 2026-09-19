"""Service protocols for later implementation stages."""

from collections.abc import Sequence
from typing import Protocol

from app.domain.emergency import EmergencyMission
from app.domain.event import TrafficEvent
from app.domain.metrics import TrafficMetrics
from app.domain.network import Network
from app.domain.optimization import OptimizationResult, OptimizationType
from app.domain.route import Route
from app.domain.scenario import Scenario


class ScenarioService(Protocol):
    def load(self, scenario_id: str, seed: int) -> Scenario: ...

    def current(self) -> Scenario | None: ...


class SimulationService(Protocol):
    def start(self, scenario: Scenario) -> Scenario: ...

    def pause(self, scenario: Scenario) -> Scenario: ...

    def step(self, scenario: Scenario, seconds: float) -> Scenario: ...


class OptimizationService(Protocol):
    def optimize(
        self,
        scenario: Scenario,
        optimization_type: OptimizationType,
    ) -> OptimizationResult: ...


class EmergencyService(Protocol):
    def create_mission(
        self,
        scenario: Scenario,
        mission: EmergencyMission,
    ) -> EmergencyMission: ...

    def restore(self, scenario: Scenario, mission_id: str) -> Scenario: ...


class EventService(Protocol):
    def schedule(self, scenario: Scenario, event: TrafficEvent) -> TrafficEvent: ...

    def resolve(self, scenario: Scenario, event_id: str) -> TrafficEvent: ...


class ExperimentService(Protocol):
    def run(self, scenario: Scenario) -> Sequence[TrafficMetrics]: ...


class RoutingService(Protocol):
    def load_network(self, mode: str) -> Network: ...

    def candidate_routes(
        self,
        network: Network,
        origin: str,
        destination: str,
        *,
        max_candidates: int = 3,
    ) -> tuple[Route, ...]: ...
