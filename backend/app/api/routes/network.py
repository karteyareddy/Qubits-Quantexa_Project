"""Network topology endpoints."""

from fastapi import APIRouter

from app.api.schemas.network import EdgeSchema, IntersectionSchema, NetworkSchema
from app.routing.demo_network import build_demo_network

network_router = APIRouter(prefix="/network", tags=["Network"])


@network_router.get("", response_model=NetworkSchema)
def get_network() -> NetworkSchema:
    """Expose the deterministic 6-intersection demo network topology."""
    network = build_demo_network(seed=42)

    sorted_nodes = sorted(network.nodes, key=lambda n: n.node_id)
    signalized = [n.node_id for n in sorted_nodes if n.is_intersection]

    intersections = [
        IntersectionSchema(
            intersection_id=node.node_id,
            name=f"Intersection {node.node_id}",
            is_signalized=node.is_intersection,
        )
        for node in sorted_nodes
    ]

    edges = [
        EdgeSchema(
            edge_id=edge.edge_id,
            source_intersection=edge.source,
            target_intersection=edge.target,
            free_flow_travel_time_seconds=edge.travel_time_seconds,
            capacity=edge.capacity,
            length_meters=edge.length_m,
        )
        for edge in network.edges
    ]

    return NetworkSchema(
        intersections=intersections,
        edges=edges,
        signalized_intersections=signalized,
    )
