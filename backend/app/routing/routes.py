"""Deterministic candidate route generation."""

from itertools import islice, pairwise
from typing import cast

import networkx as nx

from app.core.errors import RouteNotFoundError
from app.domain.network import Network
from app.domain.route import Route
from app.routing.normalization import network_to_routing_graph, validate_network


def generate_candidate_routes(
    network: Network,
    origin: str,
    destination: str,
    *,
    max_candidates: int = 3,
) -> tuple[Route, ...]:
    """Return bounded travel-time-ordered routes or raise an explicit error."""
    if max_candidates < 1:
        raise ValueError("max_candidates must be at least one")
    validate_network(network)
    graph = network_to_routing_graph(network)
    if origin not in graph or destination not in graph:
        raise RouteNotFoundError("route endpoints must exist in the network")
    if origin == destination:
        return (
            Route(
                route_id=f"route:{origin}:{destination}:0",
                node_ids=(origin,),
                estimated_travel_time_seconds=0.0,
                distance_m=0.0,
                cost=0.0,
            ),
        )

    try:
        paths = nx.shortest_simple_paths(
            graph,
            source=origin,
            target=destination,
            weight="travel_time_seconds",
        )
        node_paths = tuple(islice(paths, max_candidates))
    except (nx.NetworkXNoPath, nx.NodeNotFound) as exc:
        raise RouteNotFoundError(f"no route from {origin} to {destination}") from exc

    if not node_paths:
        raise RouteNotFoundError(f"no route from {origin} to {destination}")

    routes = tuple(
        _build_route(graph, tuple(cast(list[str], node_path)), origin, destination, index)
        for index, node_path in enumerate(node_paths)
    )
    return tuple(
        sorted(
            routes,
            key=lambda route: (
                route.estimated_travel_time_seconds,
                route.node_ids,
                route.edge_ids,
            ),
        )
    )


def shortest_route(network: Network, origin: str, destination: str) -> Route:
    return generate_candidate_routes(
        network,
        origin,
        destination,
        max_candidates=1,
    )[0]


def _build_route(
    graph: nx.DiGraph | nx.Graph,
    node_ids: tuple[str, ...],
    origin: str,
    destination: str,
    index: int,
) -> Route:
    edge_ids: list[str] = []
    distance_m = 0.0
    travel_time_seconds = 0.0
    for source, target in pairwise(node_ids):
        edge = graph.get_edge_data(source, target)
        if edge is None:
            raise RouteNotFoundError("candidate path contains a missing edge")
        edge_ids.append(cast(str, edge["edge_id"]))
        distance_m += cast(float, edge["length_m"])
        travel_time_seconds += cast(float, edge["travel_time_seconds"])

    return Route(
        route_id=f"route:{origin}:{destination}:{index}",
        node_ids=node_ids,
        edge_ids=tuple(edge_ids),
        estimated_travel_time_seconds=travel_time_seconds,
        distance_m=distance_m,
        cost=travel_time_seconds,
    )
