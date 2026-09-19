"""Tests for deterministic candidate route generation."""

import pytest
from app.core.errors import RouteNotFoundError
from app.domain.network import Network, NetworkNode
from app.routing.demo_network import build_demo_network
from app.routing.routes import generate_candidate_routes


def test_candidate_routes_are_valid_and_travel_time_ordered() -> None:
    network = build_demo_network(seed=42)
    routes = generate_candidate_routes(network, "I1", "I6", max_candidates=3)
    node_ids = {node.node_id for node in network.nodes}
    edge_ids = {edge.edge_id for edge in network.edges}

    assert len(routes) == 3
    assert [route.estimated_travel_time_seconds for route in routes] == sorted(
        route.estimated_travel_time_seconds for route in routes
    )
    for route in routes:
        assert set(route.node_ids).issubset(node_ids)
        assert set(route.edge_ids).issubset(edge_ids)
        assert len(route.edge_ids) == len(route.node_ids) - 1
        assert route.distance_m > 0


def test_candidate_routes_are_deterministic() -> None:
    network = build_demo_network(seed=42)

    first = generate_candidate_routes(network, "I1", "I6", max_candidates=3)
    second = generate_candidate_routes(network, "I1", "I6", max_candidates=3)

    assert first == second


def test_disconnected_network_raises_instead_of_fabricating_direct_edge() -> None:
    network = Network(
        network_id="disconnected",
        directed=True,
        nodes=(NetworkNode(node_id="I1"), NetworkNode(node_id="I2")),
    )

    with pytest.raises(RouteNotFoundError, match="no route"):
        generate_candidate_routes(network, "I1", "I2")
