"""Small routing service coordinating providers and candidate generation."""

from collections.abc import Mapping

from app.core.errors import NetworkProviderError
from app.domain.network import Network
from app.domain.route import Route
from app.routing.normalization import validate_network
from app.routing.providers import NetworkProvider
from app.routing.routes import generate_candidate_routes


class DefaultRoutingService:
    def __init__(self, providers: Mapping[str, NetworkProvider]) -> None:
        self._providers = dict(providers)

    def load_network(self, mode: str) -> Network:
        provider = self._providers.get(mode)
        if provider is None:
            raise NetworkProviderError(f"unknown network provider mode: {mode}")
        network = provider.load_network()
        validate_network(network)
        return network

    def candidate_routes(
        self,
        network: Network,
        origin: str,
        destination: str,
        *,
        max_candidates: int = 3,
    ) -> tuple[Route, ...]:
        return generate_candidate_routes(
            network,
            origin,
            destination,
            max_candidates=max_candidates,
        )
