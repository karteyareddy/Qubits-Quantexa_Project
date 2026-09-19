"""Shared Stage 2 unit-test fixtures."""

import pytest
from app.domain.network import Network, NetworkEdge, NetworkNode
from app.domain.route import Route


@pytest.fixture
def sample_route() -> Route:
    return Route(
        route_id="route-1",
        node_ids=("I1", "I2"),
        edge_ids=("E1",),
        estimated_travel_time_seconds=30.0,
        distance_m=250.0,
        cost=1.0,
    )


@pytest.fixture
def sample_network() -> Network:
    return Network(
        network_id="network-1",
        scenario_id="scenario-1",
        directed=True,
        nodes=(NetworkNode(node_id="I1"), NetworkNode(node_id="I2")),
        edges=(
            NetworkEdge(
                edge_id="E1",
                source="I1",
                target="I2",
                length_m=250.0,
                capacity=20.0,
                free_flow_speed_kph=40.0,
                travel_time_seconds=30.0,
            ),
        ),
    )
