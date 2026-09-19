"""Deterministic offline six-intersection network provider."""

from dataclasses import dataclass

from app.domain.network import Coordinates, Network, NetworkEdge, NetworkNode
from app.routing.normalization import calculate_travel_time_seconds, validate_network

DEMO_CONNECTIONS = (
    ("I1", "I2", 500.0, 40.0, 24.0),
    ("I2", "I3", 500.0, 40.0, 24.0),
    ("I4", "I5", 500.0, 40.0, 24.0),
    ("I5", "I6", 500.0, 40.0, 24.0),
    ("I1", "I4", 400.0, 30.0, 18.0),
    ("I2", "I5", 400.0, 30.0, 18.0),
    ("I3", "I6", 400.0, 30.0, 18.0),
)

DEMO_NODE_POSITIONS = {
    "I1": (0.0, 1.0, 9.9700, 76.2400),
    "I2": (1.0, 1.0, 9.9700, 76.2450),
    "I3": (2.0, 1.0, 9.9700, 76.2500),
    "I4": (0.0, 0.0, 9.9660, 76.2400),
    "I5": (1.0, 0.0, 9.9660, 76.2450),
    "I6": (2.0, 0.0, 9.9660, 76.2500),
}


def build_demo_network(*, seed: int = 42) -> Network:
    """Build the fully offline demo network without global random state."""
    nodes = tuple(
        NetworkNode(
            node_id=node_id,
            x=x,
            y=y,
            coordinates=Coordinates(latitude=latitude, longitude=longitude),
            metadata={"label": node_id},
        )
        for node_id, (x, y, latitude, longitude) in DEMO_NODE_POSITIONS.items()
    )

    edges: list[NetworkEdge] = []
    for source, target, length_m, speed_kph, capacity in DEMO_CONNECTIONS:
        for edge_source, edge_target in ((source, target), (target, source)):
            edges.append(
                NetworkEdge(
                    edge_id=f"{edge_source}->{edge_target}",
                    source=edge_source,
                    target=edge_target,
                    length_m=length_m,
                    capacity=capacity,
                    free_flow_speed_kph=speed_kph,
                    travel_time_seconds=calculate_travel_time_seconds(
                        length_m,
                        speed_kph,
                    ),
                    congestion=0.0,
                    metadata={"road_pair": f"{source}-{target}"},
                )
            )

    network = Network(
        network_id="demo-6-intersection",
        scenario_id="demo-6-intersection",
        directed=True,
        nodes=nodes,
        edges=tuple(edges),
        metadata={"provider": "demo", "seed": seed},
    )
    validate_network(network, require_connected=True)
    return network


@dataclass(frozen=True)
class DemoNetworkProvider:
    """Provider adapter for the deterministic offline network."""

    seed: int = 42

    def load_network(self) -> Network:
        return build_demo_network(seed=self.seed)
