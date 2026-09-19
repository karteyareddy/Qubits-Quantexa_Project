"""Optional OSMnx network provider with explicit offline fallback."""

from collections.abc import Callable
from dataclasses import dataclass, field
from importlib import import_module
from typing import Protocol, cast

import networkx as nx

from app.core.errors import NetworkError, NetworkProviderError
from app.domain.network import Network
from app.routing.cache import NetworkCache
from app.routing.normalization import normalize_networkx_graph, validate_network
from app.routing.providers import NetworkProvider


class _OSMnxModule(Protocol):
    def geocode(self, query: str) -> tuple[float, float]: ...

    def graph_from_point(
        self,
        center_point: tuple[float, float],
        *,
        dist: float,
        network_type: str,
        simplify: bool,
    ) -> nx.MultiDiGraph: ...

    def graph_from_place(
        self,
        query: str,
        *,
        network_type: str,
        simplify: bool,
    ) -> nx.MultiDiGraph: ...


def _load_osmnx() -> _OSMnxModule:
    try:
        return cast(_OSMnxModule, import_module("osmnx"))
    except ImportError as exc:
        raise NetworkProviderError(
            "OSM mode requires the optional requirements-osm.txt dependencies"
        ) from exc


@dataclass(frozen=True)
class OSMNetworkProvider:
    """Load and normalize a directed OSM road graph."""

    place_name: str
    distance_m: float = 1500.0
    cache: NetworkCache | None = None
    fallback_provider: NetworkProvider | None = None
    module_loader: Callable[[], _OSMnxModule] = field(
        default=_load_osmnx,
        repr=False,
        compare=False,
    )

    def load_network(self) -> Network:
        place_name = self.place_name.strip()
        if not place_name:
            raise NetworkProviderError("OSM place name cannot be empty")
        if self.distance_m <= 0:
            raise NetworkProviderError("OSM distance must be positive")

        cache_key = f"osm:{place_name}:{self.distance_m}:drive"
        if self.cache is not None:
            cached = self.cache.load(cache_key)
            if cached is not None:
                validate_network(cached)
                return cached

        try:
            module = self.module_loader()
            graph = self._load_graph(module, place_name)
            network = normalize_networkx_graph(
                graph,
                network_id=f"osm:{place_name}",
            )
            validate_network(network)
        except Exception as exc:
            if self.fallback_provider is not None:
                return self.fallback_provider.load_network()
            if isinstance(exc, NetworkError):
                raise
            raise NetworkProviderError(f"unable to load OSM network: {exc}") from exc

        if self.cache is not None:
            self.cache.save(cache_key, network)
        return network

    def _load_graph(self, module: _OSMnxModule, place_name: str) -> nx.MultiDiGraph:
        try:
            center_point = module.geocode(place_name)
            return module.graph_from_point(
                center_point,
                dist=self.distance_m,
                network_type="drive",
                simplify=True,
            )
        except (OSError, RuntimeError, ValueError) as point_error:
            try:
                return module.graph_from_place(
                    place_name,
                    network_type="drive",
                    simplify=True,
                )
            except (OSError, RuntimeError, ValueError) as place_error:
                raise NetworkProviderError(
                    "OSM point and place network acquisition both failed: "
                    f"point={point_error}; place={place_error}"
                ) from place_error
