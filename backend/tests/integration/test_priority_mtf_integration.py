"""Integration test coupling Stage 3 Demo Network & Routing with Stage 7 MTF Optimizer."""

from app.domain.vehicle import EmergencySubtype, Vehicle, VehicleType
from app.optimization.service import PriorityMTFOptimizerService
from app.routing.demo_network import DemoNetworkProvider
from app.routing.routes import generate_candidate_routes


def test_priority_mtf_optimizer_with_demo_network_and_routes() -> None:
    network_provider = DemoNetworkProvider()
    network = network_provider.load_network()

    v1 = Vehicle(
        vehicle_id="v1",
        vehicle_type=VehicleType.REGULAR,
        origin="I1",
        destination="I6",
        priority_weight=1,
    )
    v_em = Vehicle(
        vehicle_id="v_em",
        vehicle_type=VehicleType.EMERGENCY,
        origin="I1",
        destination="I6",
        is_emergency=True,
        emergency_subtype=EmergencySubtype.AMBULANCE,
        priority_weight=10,
    )

    r1 = generate_candidate_routes(network, "I1", "I6", max_candidates=3)
    candidate_map = {
        "v1": tuple(r.node_ids for r in r1),
        "v_em": tuple(r.node_ids for r in r1),
    }

    optimizer = PriorityMTFOptimizerService()
    result = optimizer.optimize(
        "opt-demo-1",
        network,
        (v1, v_em),
        candidate_map,
        method="exact",
    )

    assert result.feasible is True
    assert result.decoded_plan is not None
    assert "v1" in result.decoded_plan.decisions
    assert "v_em" in result.decoded_plan.decisions
    assert result.objective_value is not None
    assert result.objective_value > 0.0

