"""Integration coverage across Stage 3 routing and Stage 4 simulation."""

from app.simulation.engine import TrafficSimulation
from app.simulation.scenarios import low_traffic_scenario


def test_simulation_uses_demo_network_routes_for_sixty_seconds() -> None:
    scenario = low_traffic_scenario(seed=42)
    simulation = TrafficSimulation(scenario)

    state = simulation.run(60.0)

    valid_edge_ids = {edge.edge_id for edge in scenario.network.edges}
    occupied_edge_ids = {
        vehicle.current_edge_id
        for vehicle in state.active_vehicles
        if vehicle.current_edge_id is not None
    }
    assert scenario.network.network_id == "demo-6-intersection"
    assert state.simulation_time_seconds == 60.0
    assert occupied_edge_ids.issubset(valid_edge_ids)
    assert state.counts.active + state.counts.completed == 3
