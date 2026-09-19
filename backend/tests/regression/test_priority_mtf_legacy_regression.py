"""Regression test comparing legacy priority_aware_mtf.py with Stage 7 backend optimizer."""

import sys
from pathlib import Path

# Add project root to sys.path to allow importing legacy priority_aware_mtf.py
root_dir = Path(__file__).resolve().parents[3]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.domain.vehicle import EmergencySubtype, Vehicle, VehicleType
from app.optimization.objective import PriorityMTFConfig
from app.optimization.service import PriorityMTFOptimizerService
from app.routing.demo_network import DemoNetworkProvider

from priority_aware_mtf import priority_aware_mtf_solve


def test_migrated_mtf_matches_legacy_implementation_route_decisions() -> None:
    network_provider = DemoNetworkProvider()
    network = network_provider.load_network()

    # Create NetworkX graph matching legacy format
    import networkx as nx

    graph = nx.DiGraph()
    for node in network.nodes:
        graph.add_node(node.node_id)
    for edge in network.edges:
        graph.add_edge(
            edge.source,
            edge.target,
            travel_time=edge.travel_time_seconds,
            length=1000.0,
            speed=40.0,
            congestion=0,
        )

    legacy_vehicles = [
        {
            "vehicle_id": "v1",
            "type": "regular",
            "origin": "I1",
            "destination": "I6",
            "priority_weight": 1,
            "candidate_routes": [
                ["I1", "I2", "I3", "I6"],
                ["I1", "I4", "I5", "I6"],
            ],
        },
        {
            "vehicle_id": "v2",
            "type": "regular",
            "origin": "I1",
            "destination": "I6",
            "priority_weight": 1,
            "candidate_routes": [
                ["I1", "I2", "I3", "I6"],
                ["I1", "I4", "I5", "I6"],
            ],
        },
        {
            "vehicle_id": "v_em",
            "type": "emergency",
            "origin": "I1",
            "destination": "I6",
            "priority_weight": 10,
            "candidate_routes": [
                ["I1", "I2", "I3", "I6"],
                ["I1", "I4", "I5", "I6"],
            ],
        },
    ]

    domain_vehicles = [
        Vehicle(
            vehicle_id="v1",
            vehicle_type=VehicleType.REGULAR,
            origin="I1",
            destination="I6",
            priority_weight=1,
        ),
        Vehicle(
            vehicle_id="v2",
            vehicle_type=VehicleType.REGULAR,
            origin="I1",
            destination="I6",
            priority_weight=1,
        ),
        Vehicle(
            vehicle_id="v_em",
            vehicle_type=VehicleType.EMERGENCY,
            origin="I1",
            destination="I6",
            is_emergency=True,
            emergency_subtype=EmergencySubtype.AMBULANCE,
            priority_weight=10,
        ),
    ]

    candidate_map = {
        "v1": (("I1", "I2", "I3", "I6"), ("I1", "I4", "I5", "I6")),
        "v2": (("I1", "I2", "I3", "I6"), ("I1", "I4", "I5", "I6")),
        "v_em": (("I1", "I2", "I3", "I6"), ("I1", "I4", "I5", "I6")),
    }

    # Run legacy solve
    legacy_routes, legacy_metrics = priority_aware_mtf_solve(
        legacy_vehicles,
        graph,
        method="exact",
        num_iterations=1,
        gamma=50.0,
        emergency_boost=10.0,
    )

    # Run migrated solve
    service = PriorityMTFOptimizerService(
        config=PriorityMTFConfig(gamma=50.0, num_iterations=1)
    )
    migrated_result = service.optimize(
        "opt-regression-1",
        network,
        domain_vehicles,
        candidate_map,
        method="exact",
    )

    assert migrated_result.feasible is True
    assert migrated_result.decoded_plan is not None

    migrated_decisions = migrated_result.decoded_plan.decisions
    for vid, legacy_route in legacy_routes.items():
        assert vid in migrated_decisions
        assert list(migrated_decisions[vid]) == list(legacy_route)

    solution_metrics = migrated_result.metadata.get("solution_metrics", {})
    assert solution_metrics.get("emergency_vehicles_routed") == legacy_metrics[
        "emergency_vehicles_routed"
    ]
    assert solution_metrics.get("regular_vehicles_routed") == legacy_metrics[
        "regular_vehicles_routed"
    ]
