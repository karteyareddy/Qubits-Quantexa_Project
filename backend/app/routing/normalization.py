"""NetworkX-to-domain normalization and structural validation."""

from collections.abc import Iterable, Mapping
from typing import cast

import networkx as nx
from pydantic import JsonValue, ValidationError

from app.core.errors import NetworkValidationError
from app.domain.network import Coordinates, Network, NetworkEdge, NetworkNode

DEFAULT_CAPACITY = 20.0
DEFAULT_SPEED_KPH = 40.0


def calculate_travel_time_seconds(
    length_m: float,
    speed_kph: float,
    congestion: float = 0.0,
) -> float:
    """Preserve the legacy congestion multiplier with seconds as the unit."""
    if length_m <= 0:
        raise NetworkValidationError("edge length must be positive")
    if speed_kph <= 0:
        raise NetworkValidationError("edge speed must be positive")
    if congestion < 0:
        raise NetworkValidationError("edge congestion cannot be negative")
    base_seconds = length_m / (speed_kph * 1000.0 / 3600.0)
    return base_seconds * (1.0 + congestion / 20.0)


def normalize_networkx_graph(
    graph: nx.Graph,
    *,
    network_id: str,
    scenario_id: str | None = None,
    default_capacity: float = DEFAULT_CAPACITY,
    default_speed_kph: float = DEFAULT_SPEED_KPH,
) -> Network:
    """Normalize a NetworkX graph without discarding direction or parallel edges."""
    if default_capacity <= 0:
        raise NetworkValidationError("default capacity must be positive")
    if default_speed_kph <= 0:
        raise NetworkValidationError("default speed must be positive")

    nodes = tuple(
        _normalize_node(node_id, data)
        for node_id, data in sorted(graph.nodes(data=True), key=lambda item: str(item[0]))
    )
    edges = tuple(
        _normalize_edge(
            source,
            target,
            key,
            data,
            default_capacity=default_capacity,
            default_speed_kph=default_speed_kph,
        )
        for source, target, key, data in _iter_edges(graph)
    )

    try:
        network = Network(
            network_id=network_id,
            scenario_id=scenario_id,
            directed=graph.is_directed(),
            nodes=nodes,
            edges=tuple(sorted(edges, key=lambda edge: edge.edge_id)),
            metadata={"source": "networkx", "multigraph": graph.is_multigraph()},
        )
    except ValidationError as exc:
        raise NetworkValidationError(f"invalid normalized network: {exc}") from exc

    validate_network(network)
    return network


def validate_network(network: Network, *, require_connected: bool = False) -> None:
    """Validate graph-level invariants not expressible on individual fields."""
    if not network.nodes:
        raise NetworkValidationError("network requires at least one node")

    if require_connected:
        graph = network_to_multigraph(network)
        if network.directed:
            connected = nx.is_weakly_connected(cast(nx.MultiDiGraph, graph))
        else:
            connected = nx.is_connected(cast(nx.MultiGraph, graph))
        if not connected:
            raise NetworkValidationError("network must be connected")


def network_to_multigraph(network: Network) -> nx.MultiDiGraph | nx.MultiGraph:
    """Convert a domain network to NetworkX while retaining parallel edges."""
    graph: nx.MultiDiGraph | nx.MultiGraph
    graph = nx.MultiDiGraph() if network.directed else nx.MultiGraph()
    for node in sorted(network.nodes, key=lambda item: item.node_id):
        graph.add_node(
            node.node_id,
            x=node.x,
            y=node.y,
            coordinates=node.coordinates,
            is_intersection=node.is_intersection,
            metadata=node.metadata,
        )
    for edge in sorted(network.edges, key=lambda item: item.edge_id):
        graph.add_edge(
            edge.source,
            edge.target,
            key=edge.edge_id,
            edge_id=edge.edge_id,
            length_m=edge.length_m,
            capacity=edge.capacity,
            free_flow_speed_kph=edge.free_flow_speed_kph,
            travel_time_seconds=edge.travel_time_seconds,
            congestion=edge.congestion,
            closed=edge.closed,
            metadata=edge.metadata,
        )
    return graph


def network_to_routing_graph(network: Network) -> nx.DiGraph | nx.Graph:
    """Collapse parallel edges by fastest travel time for node-path routing.

    The domain contract retains every parallel edge. Candidate node-path routing
    deterministically selects the fastest open edge per source/target pair and
    uses edge identity as the tie-breaker.
    """
    graph: nx.DiGraph | nx.Graph
    graph = nx.DiGraph() if network.directed else nx.Graph()
    for node in sorted(network.nodes, key=lambda item: item.node_id):
        graph.add_node(node.node_id)

    for edge in sorted(network.edges, key=lambda item: item.edge_id):
        if edge.closed:
            continue
        candidate = (edge.travel_time_seconds, edge.edge_id)
        existing = graph.get_edge_data(edge.source, edge.target)
        if existing is not None:
            current = (
                cast(float, existing["travel_time_seconds"]),
                cast(str, existing["edge_id"]),
            )
            if candidate >= current:
                continue
        graph.add_edge(
            edge.source,
            edge.target,
            edge_id=edge.edge_id,
            length_m=edge.length_m,
            travel_time_seconds=edge.travel_time_seconds,
        )
    return graph


def _normalize_node(node_id: object, data: Mapping[str, object]) -> NetworkNode:
    x = _optional_float(data.get("x"))
    y = _optional_float(data.get("y"))
    coordinates = None
    if x is not None and y is not None and -180 <= x <= 180 and -90 <= y <= 90:
        coordinates = Coordinates(latitude=y, longitude=x)
    street_count = _optional_float(data.get("street_count"))
    is_intersection = street_count is None or street_count >= 2
    return NetworkNode(
        node_id=str(node_id),
        is_intersection=is_intersection,
        x=x,
        y=y,
        coordinates=coordinates,
        metadata=_select_metadata(data, ("highway", "ref", "street_count")),
    )


def _normalize_edge(
    source: object,
    target: object,
    key: object,
    data: Mapping[str, object],
    *,
    default_capacity: float,
    default_speed_kph: float,
) -> NetworkEdge:
    source_id = str(source)
    target_id = str(target)
    edge_id = str(data.get("edge_id") or f"{source_id}->{target_id}:{key}")
    length_m = _required_positive_float(data.get("length_m", data.get("length")), "length")
    capacity = _required_positive_float(data.get("capacity", default_capacity), "capacity")
    speed = _parse_speed(data, default_speed_kph)
    congestion = _required_non_negative_float(data.get("congestion", 0.0), "congestion")
    travel_time = _optional_float(
        data.get("travel_time_seconds", data.get("travel_time"))
    )
    if travel_time is None:
        travel_time = calculate_travel_time_seconds(length_m, speed, congestion)
    if travel_time < 0:
        raise NetworkValidationError("edge travel time cannot be negative")

    return NetworkEdge(
        edge_id=edge_id,
        source=source_id,
        target=target_id,
        length_m=length_m,
        capacity=capacity,
        free_flow_speed_kph=speed,
        travel_time_seconds=travel_time,
        congestion=congestion,
        closed=bool(data.get("closed", False)),
        metadata=_select_metadata(
            data,
            ("name", "highway", "osmid", "oneway", "lanes", "maxspeed"),
        ),
    )


def _iter_edges(
    graph: nx.Graph | nx.DiGraph | nx.MultiGraph | nx.MultiDiGraph,
) -> tuple[tuple[object, object, object, Mapping[str, object]], ...]:
    if isinstance(graph, (nx.MultiGraph, nx.MultiDiGraph)):
        edges = cast(
            Iterable[tuple[object, object, object, Mapping[str, object]]],
            graph.edges(keys=True, data=True),
        )
    else:
        basic_edges = cast(
            Iterable[tuple[object, object, Mapping[str, object]]],
            graph.edges(data=True),
        )
        edges = ((source, target, 0, data) for source, target, data in basic_edges)
    return tuple(sorted(edges, key=lambda item: (str(item[0]), str(item[1]), str(item[2]))))


def _parse_speed(data: Mapping[str, object], default_speed_kph: float) -> float:
    raw_speed = data.get("speed_kph", data.get("speed", data.get("maxspeed")))
    if isinstance(raw_speed, (list, tuple)):
        raw_speed = raw_speed[0] if raw_speed else None
    if isinstance(raw_speed, str):
        numeric = raw_speed.lower().replace("km/h", "").strip().split()[0]
        try:
            raw_speed = float(numeric)
        except ValueError:
            raw_speed = None
    if raw_speed is None:
        raw_speed = default_speed_kph
    return _required_positive_float(raw_speed, "speed")


def _optional_float(value: object) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(cast(float | int | str, value))
    except (TypeError, ValueError):
        return None


def _required_positive_float(value: object, name: str) -> float:
    parsed = _optional_float(value)
    if parsed is None or parsed <= 0:
        raise NetworkValidationError(f"edge {name} must be positive")
    return parsed


def _required_non_negative_float(value: object, name: str) -> float:
    parsed = _optional_float(value)
    if parsed is None or parsed < 0:
        raise NetworkValidationError(f"edge {name} cannot be negative")
    return parsed


def _select_metadata(
    data: Mapping[str, object],
    keys: tuple[str, ...],
) -> dict[str, JsonValue]:
    metadata: dict[str, JsonValue] = {}
    for key in keys:
        if key not in data:
            continue
        value = data[key]
        if value is None or isinstance(value, (str, int, float, bool)):
            metadata[key] = value
        elif isinstance(value, (list, tuple, set)):
            metadata[key] = [str(item) for item in value]
        else:
            metadata[key] = str(value)
    return metadata
