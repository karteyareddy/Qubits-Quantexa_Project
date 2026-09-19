"""Tests for the deterministic offline six-intersection network."""

import networkx as nx
from app.routing.demo_network import DEMO_CONNECTIONS, build_demo_network
from app.routing.normalization import network_to_multigraph
from app.routing.routes import shortest_route


def test_demo_network_has_expected_topology() -> None:
    network = build_demo_network(seed=42)
    expected_pairs = {frozenset((source, target)) for source, target, *_ in DEMO_CONNECTIONS}
    actual_pairs = {frozenset((edge.source, edge.target)) for edge in network.edges}

    assert len(network.nodes) == 6
    assert len(network.edges) == 14
    assert {node.node_id for node in network.nodes} == {f"I{index}" for index in range(1, 7)}
    assert actual_pairs == expected_pairs


def test_demo_network_is_connected_and_bidirectionally_routable() -> None:
    network = build_demo_network(seed=42)
    graph = network_to_multigraph(network)

    assert isinstance(graph, nx.MultiDiGraph)
    assert nx.is_strongly_connected(graph)
    assert shortest_route(network, "I1", "I6").node_ids[0] == "I1"
    assert shortest_route(network, "I6", "I1").node_ids[0] == "I6"


def test_demo_network_is_deterministic() -> None:
    first = build_demo_network(seed=42)
    second = build_demo_network(seed=42)

    assert first.model_dump(mode="json") == second.model_dump(mode="json")
    assert first.nodes[0].x == 0.0
    assert first.nodes[0].coordinates is not None
    assert first.edges[0].travel_time_seconds == second.edges[0].travel_time_seconds
