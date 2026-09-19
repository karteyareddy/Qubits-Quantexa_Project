"""Regression coverage for useful legacy network-builder semantics."""

import pytest
from app.routing.demo_network import build_demo_network
from app.routing.normalization import calculate_travel_time_seconds
from app.routing.routes import generate_candidate_routes


def test_travel_time_matches_legacy_formula_with_seconds_unit() -> None:
    travel_time_seconds = calculate_travel_time_seconds(
        length_m=1000.0,
        speed_kph=60.0,
        congestion=10.0,
    )

    assert travel_time_seconds == pytest.approx(90.0)


def test_congestion_increases_travel_time_monotonically() -> None:
    free_flow = calculate_travel_time_seconds(500.0, 40.0, congestion=0.0)
    congested = calculate_travel_time_seconds(500.0, 40.0, congestion=10.0)

    assert congested > free_flow


def test_candidate_routes_use_travel_time_weight() -> None:
    network = build_demo_network(seed=42)
    routes = generate_candidate_routes(network, "I1", "I6", max_candidates=3)

    assert routes[0].estimated_travel_time_seconds <= routes[1].estimated_travel_time_seconds
    assert routes[1].estimated_travel_time_seconds <= routes[2].estimated_travel_time_seconds
