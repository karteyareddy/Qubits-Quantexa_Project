"""Domain validation helpers and input boundary checks."""

from app.domain.network import Network
from app.events.models import TrafficEventBase


class ValidationError(Exception):
    """Exception raised when public input validation fails."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def validate_network_node_exists(network: Network, node_id: str) -> str:
    """Validate that node_id exists in network topology."""
    node_ids = {node.node_id for node in network.nodes}
    if node_id not in node_ids:
        raise ValidationError(f"Intersection / Node '{node_id}' does not exist in network topology.")
    return node_id


def validate_network_edge_exists(network: Network, edge_id: str) -> str:
    """Validate that edge_id exists in network topology."""
    edge_ids = {edge.edge_id for edge in network.edges}
    if edge_id not in edge_ids:
        raise ValidationError(f"Network Edge '{edge_id}' does not exist in network topology.")
    return edge_id


def validate_event_payload(event: TrafficEventBase, network: Network) -> TrafficEventBase:
    """Validate event parameters against network topology and timestamps."""
    if event.starts_at_seconds < 0.0:
        raise ValidationError(f"Event '{event.event_id}' has negative start timestamp.")

    if event.duration_seconds is not None and event.duration_seconds <= 0.0:
        raise ValidationError(f"Event '{event.event_id}' duration must be positive.")

    # Validate target edge/origin node
    if hasattr(event, "edge_id") and event.edge_id:
        validate_network_edge_exists(network, str(event.edge_id))

    if hasattr(event, "origin") and event.origin:
        validate_network_node_exists(network, str(event.origin))

    if hasattr(event, "destination") and event.destination:
        validate_network_node_exists(network, str(event.destination))

    return event
