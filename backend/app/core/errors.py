"""Typed domain and service errors."""


class DomainError(Exception):
    """Base error for expected backend domain failures."""

    code = "domain_error"

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class DomainValidationError(DomainError):
    code = "validation_error"


class NetworkError(DomainError):
    code = "network_error"


class NetworkValidationError(NetworkError):
    code = "network_validation_error"


class NetworkProviderError(NetworkError):
    code = "network_provider_error"


class RouteNotFoundError(NetworkError):
    code = "route_not_found"


class ScenarioError(DomainError):
    code = "scenario_error"


class OptimizationError(DomainError):
    code = "optimization_error"


class SimulationError(DomainError):
    code = "simulation_error"
