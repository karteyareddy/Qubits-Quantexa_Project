"""Integration test constructing Signal QUBO from live simulation state snapshot."""

from app.domain.signal import SignalPhase
from app.signals.policy import FixedTimeSignalPolicy, SignalSystem
from app.signals.qubo.builder import SignalQuboBuilder
from app.signals.qubo.config import SignalQuboConfig
from app.signals.qubo.decoder import decode_signal_qubo_solution
from app.signals.qubo.evaluator import evaluate_qubo_energy
from app.signals.qubo.reference_solver import solve_signal_qubo_brute_force
from app.simulation.engine import TrafficSimulation
from app.simulation.scenarios import congested_traffic_scenario


def test_signal_qubo_builder_on_congested_demo_simulation_snapshot() -> None:
    scenario = congested_traffic_scenario(seed=42)
    policy = FixedTimeSignalPolicy(SignalSystem.for_network(scenario.network))
    simulation = TrafficSimulation(scenario, entry_policy=policy)
    for _ in range(30):
        simulation.step()

    state = simulation.state
    network = scenario.network
    config = SignalQuboConfig(horizon_intervals=2, constraint_penalty=100.0)

    builder = SignalQuboBuilder(config=config)
    Q1, off1, vars1, map1 = builder.build_qubo(network, state)
    Q2, off2, vars2, map2 = builder.build_qubo(network, state)

    assert Q1 == Q2
    assert off1 == off2
    assert vars1 == vars2
    assert map1 == map2

    # Verify problem dimensions: 6 intersections * 2 phases * 2 intervals = 24 variables
    assert len(vars1) == 24
    assert len(Q1) > 0

    # Test single-intersection subproblem brute-force solve for ground-truth validation
    valid_node_ids = {"I1"}
    single_net = scenario.network.model_copy(
        update={
            "nodes": tuple(n for n in scenario.network.nodes if n.node_id in valid_node_ids),
            "edges": tuple(
                e for e in scenario.network.edges
                if e.source in valid_node_ids and e.target in valid_node_ids
            ),
        }
    )
    Q_single, off_s, vars_s, map_s = builder.build_qubo(single_net, state)

    best_sample, min_energy, _bitstring = solve_signal_qubo_brute_force(
        Q_single, vars_s, off_s
    )

    legal_phases = {
        n.node_id: (SignalPhase.EW_GREEN, SignalPhase.NS_GREEN)
        for n in single_net.nodes
        if n.is_intersection
    }

    schedule, feasibility, _bit = decode_signal_qubo_solution(
        best_sample,
        map_s,
        vars_s,
        legal_phases,
        horizon_intervals=2,
    )

    assert feasibility.feasible is True
    assert schedule is not None
    assert len(schedule.decisions) == 2  # 1 intersection * 2 intervals
    assert evaluate_qubo_energy(Q_single, best_sample, off_s) == min_energy
