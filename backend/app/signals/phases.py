"""Network-derived approach mapping and phase indication rules."""

from app.domain.network import Network, NetworkNode
from app.domain.signal import SignalIndication, SignalPhase
from app.signals.models import ApproachAxis, SignalApproach


def approaches_for_network(network: Network) -> dict[str, tuple[SignalApproach, ...]]:
    """Derive incoming approaches for every intersection in stable order."""
    node_by_id = {node.node_id: node for node in network.nodes}
    approaches: dict[str, list[SignalApproach]] = {
        node.node_id: [] for node in network.nodes if node.is_intersection
    }
    incoming_by_target: dict[str, list[tuple[str, str]]] = {}
    for edge in sorted(network.edges, key=lambda item: item.edge_id):
        incoming_by_target.setdefault(edge.target, []).append((edge.edge_id, edge.source))

    for intersection_id in sorted(approaches):
        intersection = node_by_id[intersection_id]
        incoming = incoming_by_target.get(intersection_id, [])
        for fallback_index, (edge_id, source_id) in enumerate(incoming):
            axis = _approach_axis(
                node_by_id[source_id],
                intersection,
                fallback_index,
            )
            approaches[intersection_id].append(
                SignalApproach(
                    approach_id=f"{intersection_id}:{edge_id}",
                    intersection_id=intersection_id,
                    incoming_edge_id=edge_id,
                    source_node_id=source_id,
                    axis=axis,
                )
            )
    return {
        intersection_id: tuple(items)
        for intersection_id, items in approaches.items()
    }


def indication_for_phase(axis: ApproachAxis, phase: SignalPhase) -> SignalIndication:
    if phase is SignalPhase.EW_GREEN and axis is ApproachAxis.EAST_WEST:
        return SignalIndication.GREEN
    if phase is SignalPhase.NS_GREEN and axis is ApproachAxis.NORTH_SOUTH:
        return SignalIndication.GREEN
    if phase is SignalPhase.EW_YELLOW and axis is ApproachAxis.EAST_WEST:
        return SignalIndication.YELLOW
    if phase is SignalPhase.NS_YELLOW and axis is ApproachAxis.NORTH_SOUTH:
        return SignalIndication.YELLOW
    return SignalIndication.RED


def _approach_axis(
    source: NetworkNode,
    target: NetworkNode,
    fallback_index: int,
) -> ApproachAxis:
    source_position = _position(source)
    target_position = _position(target)
    if source_position is None or target_position is None:
        return (
            ApproachAxis.EAST_WEST
            if fallback_index % 2 == 0
            else ApproachAxis.NORTH_SOUTH
        )
    delta_x = target_position[0] - source_position[0]
    delta_y = target_position[1] - source_position[1]
    if abs(delta_x) >= abs(delta_y):
        return ApproachAxis.EAST_WEST
    return ApproachAxis.NORTH_SOUTH


def _position(node: NetworkNode) -> tuple[float, float] | None:
    if node.x is not None and node.y is not None:
        return node.x, node.y
    if node.coordinates is not None:
        return node.coordinates.longitude, node.coordinates.latitude
    return None
