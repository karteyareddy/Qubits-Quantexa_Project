"""Network providers, normalization, caching, and candidate routing."""

from app.routing.cache import NetworkCache
from app.routing.demo_network import DemoNetworkProvider, build_demo_network
from app.routing.normalization import (
    calculate_travel_time_seconds,
    network_to_multigraph,
    network_to_routing_graph,
    normalize_networkx_graph,
    validate_network,
)
from app.routing.providers import NetworkProvider, OSMNetworkProvider
from app.routing.routes import generate_candidate_routes, shortest_route

__all__ = [
    "DemoNetworkProvider",
    "NetworkCache",
    "NetworkProvider",
    "OSMNetworkProvider",
    "build_demo_network",
    "calculate_travel_time_seconds",
    "generate_candidate_routes",
    "network_to_multigraph",
    "network_to_routing_graph",
    "normalize_networkx_graph",
    "shortest_route",
    "validate_network",
]
