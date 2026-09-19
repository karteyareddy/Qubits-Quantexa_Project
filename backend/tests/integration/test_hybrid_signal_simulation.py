"""Integration test running Hybrid Signal Optimizer against live simulation state snapshot."""

from app.optimization.hybrid_models import HybridOptimizerConfig
from app.optimization.hybrid_service import solve_hybrid_signal_optimization
from app.quantum.config import QAOAConfig
from app.signals.policy import FixedTimeSignalPolicy, SignalSystem
from app.signals.qubo.config import SignalQuboConfig
from app.simulation.engine import TrafficSimulation
from app.simulation.scenarios import congested_traffic_scenario


def test_hybrid_signal_optimizer_integration_snapshot() -> None:
    scenario = congested_traffic_scenario(seed=42)
    policy = FixedTimeSignalPolicy(SignalSystem.for_network(scenario.network))
    sim = TrafficSimulation(scenario, entry_policy=policy)
    for _ in range(15):
        sim.step()

    # Subproblem for 1 intersection (I1)
    valid_nodes = {"I1"}
    sub_net = scenario.network.model_copy(
        update={
            "nodes": tuple(n for n in scenario.network.nodes if n.node_id in valid_nodes),
            "edges": tuple(e for e in scenario.network.edges if e.source in valid_nodes and e.target in valid_nodes),
        }
    )

    q_cfg = SignalQuboConfig(horizon_intervals=2)
    qaoa_cfg = QAOAConfig(reps=1, shots=512, seed=42, max_iterations=20)
    config = HybridOptimizerConfig(
        mode="hybrid",
        candidate_count=5,
        enable_refinement=True,
        qubo_config=q_cfg,
        qaoa_config=qaoa_cfg,
    )

    result = solve_hybrid_signal_optimization(
        network=sub_net,
        simulation_state=sim.state,
        config=config,
    )

    assert result.status in ("success", "fallback")
    assert result.is_feasible is True
    assert result.selected_schedule is not None
    assert len(result.selected_schedule.decisions) == 2
    assert result.selected_solution.qubo_energy == result.selected_energy
    assert len(result.candidates) > 0
    assert result.optimization_time > 0.0
