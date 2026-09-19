"""Tests for NetworkX normalization and validation."""

import networkx as nx
import pytest
from app.core.errors import NetworkValidationError
from app.routing.normalization import normalize_networkx_graph


def test_normalization_preserves_direction_and_parallel_edges() -> None:
    graph = nx.MultiDiGraph()
    graph.add_node(1, x=76.24, y=9.97, street_count=3)
    graph.add_node(2, x=76.25, y=9.98, street_count=2)
    graph.add_edge(1, 2, key=0, length=100.0, speed_kph=30.0, capacity=10.0)
    graph.add_edge(1, 2, key=1, length=120.0, speed_kph=40.0, capacity=12.0)
    graph.add_edge(2, 1, key=0, length=100.0, speed_kph=30.0, capacity=10.0)

    network = normalize_networkx_graph(graph, network_id="osm-fixture")

    assert network.directed is True
    assert len(network.edges) == 3
    assert len({edge.edge_id for edge in network.edges}) == 3
    assert network.nodes[0].coordinates is not None


@pytest.mark.parametrize(
    "attributes",
    [
        {"length": -1.0, "speed_kph": 30.0, "capacity": 10.0},
        {"length": 100.0, "speed_kph": 0.0, "capacity": 10.0},
        {"length": 100.0, "speed_kph": 30.0, "capacity": 0.0},
        {"speed_kph": 30.0, "capacity": 10.0},
    ],
)
def test_normalization_rejects_invalid_edge_values(attributes: dict[str, float]) -> None:
    graph = nx.DiGraph()
    graph.add_nodes_from(("I1", "I2"))
    graph.add_edge("I1", "I2", **attributes)

    with pytest.raises(NetworkValidationError):
        normalize_networkx_graph(graph, network_id="invalid")


def test_normalization_rejects_duplicate_edge_identity() -> None:
    graph = nx.MultiDiGraph()
    graph.add_nodes_from(("I1", "I2", "I3"))
    graph.add_edge("I1", "I2", edge_id="duplicate", length=100.0)
    graph.add_edge("I2", "I3", edge_id="duplicate", length=100.0)

    with pytest.raises(NetworkValidationError, match="identifiers must be unique"):
        normalize_networkx_graph(graph, network_id="invalid")
