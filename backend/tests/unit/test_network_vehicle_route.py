"""Tests for network, route, and vehicle contracts."""

import pytest
from app.domain.network import Coordinates, Network, NetworkEdge, NetworkNode
from app.domain.route import Route
from app.domain.vehicle import EmergencySubtype, Vehicle, VehicleType
from pydantic import ValidationError


def test_valid_network_supports_coordinates_and_edges(sample_network: Network) -> None:
    node = NetworkNode(
        node_id="osm-1",
        coordinates=Coordinates(latitude=9.96, longitude=76.24),
    )

    assert sample_network.directed is True
    assert sample_network.edges[0].capacity == 20.0
    assert node.coordinates is not None
    assert node.coordinates.latitude == 9.96


def test_network_rejects_invalid_edge_values() -> None:
    with pytest.raises(ValidationError):
        NetworkEdge(
            edge_id="E1",
            source="I1",
            target="I2",
            length_m=-1.0,
            capacity=20.0,
            free_flow_speed_kph=40.0,
            travel_time_seconds=30.0,
        )


def test_network_rejects_edges_with_unknown_nodes() -> None:
    with pytest.raises(ValidationError, match="existing nodes"):
        Network(
            network_id="network-1",
            directed=True,
            nodes=(NetworkNode(node_id="I1"),),
            edges=(
                NetworkEdge(
                    edge_id="E1",
                    source="I1",
                    target="missing",
                    length_m=100.0,
                    capacity=10.0,
                    free_flow_speed_kph=30.0,
                    travel_time_seconds=12.0,
                ),
            ),
        )


def test_route_rejects_empty_or_misaligned_data() -> None:
    with pytest.raises(ValidationError):
        Route(
            route_id="route-empty",
            node_ids=(),
            estimated_travel_time_seconds=0.0,
            distance_m=0.0,
        )

    with pytest.raises(ValidationError, match="edge count"):
        Route(
            route_id="route-misaligned",
            node_ids=("I1", "I2", "I3"),
            edge_ids=("E1",),
            estimated_travel_time_seconds=30.0,
            distance_m=200.0,
        )


def test_normal_vehicle_with_candidate_routes(sample_route: Route) -> None:
    vehicle = Vehicle(
        vehicle_id="vehicle-1",
        vehicle_type=VehicleType.REGULAR,
        origin="I1",
        destination="I2",
        route=sample_route,
        candidate_routes=(sample_route,),
    )

    assert vehicle.is_emergency is False
    assert vehicle.candidate_routes == (sample_route,)


def test_emergency_vehicle_requires_consistent_metadata(sample_route: Route) -> None:
    vehicle = Vehicle(
        vehicle_id="ambulance-1",
        vehicle_type=VehicleType.EMERGENCY,
        origin="I1",
        destination="I2",
        route=sample_route,
        is_emergency=True,
        emergency_subtype=EmergencySubtype.AMBULANCE,
        priority_weight=10,
    )

    assert vehicle.is_emergency is True
    assert vehicle.priority_weight == 10

    with pytest.raises(ValidationError, match="require an emergency subtype"):
        Vehicle(
            vehicle_id="invalid-emergency",
            vehicle_type=VehicleType.EMERGENCY,
            origin="I1",
            destination="I2",
            is_emergency=True,
        )
