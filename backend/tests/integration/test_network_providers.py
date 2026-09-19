"""Provider integration tests without live OSM access."""

import json
from pathlib import Path
from typing import Any

import networkx as nx
from app.domain.network import Network
from app.routing.demo_network import DemoNetworkProvider
from app.routing.providers.osm import OSMNetworkProvider
from app.services.routing import DefaultRoutingService


def load_osm_fixture() -> nx.MultiDiGraph:
    fixture_path = Path(__file__).parents[1] / "fixtures" / "osm_network.json"
    payload: dict[str, list[dict[str, Any]]] = json.loads(
        fixture_path.read_text(encoding="utf-8")
    )
    graph = nx.MultiDiGraph()
    for node in payload["nodes"]:
        node_data = dict(node)
        node_id = node_data.pop("id")
        graph.add_node(node_id, **node_data)
    for edge in payload["edges"]:
        edge_data = dict(edge)
        source = edge_data.pop("source")
        target = edge_data.pop("target")
        key = edge_data.pop("key")
        graph.add_edge(source, target, key=key, **edge_data)
    return graph


class FakeOSMnx:
    def __init__(self, graph: nx.MultiDiGraph) -> None:
        self.graph = graph

    def geocode(self, query: str) -> tuple[float, float]:
        assert query == "Fixture City"
        return (9.97, 76.24)

    def graph_from_point(
        self,
        center_point: tuple[float, float],
        *,
        dist: float,
        network_type: str,
        simplify: bool,
    ) -> nx.MultiDiGraph:
        assert center_point == (9.97, 76.24)
        assert dist == 500.0
        assert network_type == "drive"
        assert simplify is True
        return self.graph

    def graph_from_place(
        self,
        query: str,
        *,
        network_type: str,
        simplify: bool,
    ) -> nx.MultiDiGraph:
        raise AssertionError("point-based fixture load should succeed")


def test_demo_and_osm_providers_return_same_domain_contract() -> None:
    demo_provider = DemoNetworkProvider(seed=42)
    fake_osmnx = FakeOSMnx(load_osm_fixture())
    osm_provider = OSMNetworkProvider(
        place_name="Fixture City",
        distance_m=500.0,
        module_loader=lambda: fake_osmnx,
    )

    demo_network = demo_provider.load_network()
    osm_network = osm_provider.load_network()

    assert isinstance(demo_network, Network)
    assert isinstance(osm_network, Network)
    assert osm_network.directed is True
    assert all(edge.travel_time_seconds > 0 for edge in osm_network.edges)


def test_routing_service_selects_provider_and_generates_routes() -> None:
    service = DefaultRoutingService({"demo": DemoNetworkProvider(seed=42)})
    network = service.load_network("demo")
    routes = service.candidate_routes(network, "I1", "I6", max_candidates=2)

    assert network.network_id == "demo-6-intersection"
    assert len(routes) == 2
