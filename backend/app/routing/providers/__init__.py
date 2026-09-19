"""Network provider contracts and adapters."""

from typing import Protocol

from app.domain.network import Network


class NetworkProvider(Protocol):
    def load_network(self) -> Network: ...


from app.routing.providers.osm import OSMNetworkProvider

__all__ = ["NetworkProvider", "OSMNetworkProvider"]
