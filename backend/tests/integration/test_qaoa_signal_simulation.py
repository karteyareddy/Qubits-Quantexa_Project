"""Integration test running QAOA solver against Stage 8 Signal QUBO simulation snapshot."""

from app.quantum.config import QAOAConfig
from app.quantum.service import solve_signal_qubo_with_qaoa
from app.signals.policy import FixedTimeSignalPolicy, SignalSystem
from app.signals.qubo.config import SignalQuboConfig
from app.simulation.engine import TrafficSimulation
from app.simulation.scenarios import congested_traffic_scenario


def test_qaoa_solver_integration_on_subproblem_snapshot() -> None:
    scenario = congested_traffic_scenario(seed=42)
    policy = FixedTimeSignalPolicy(SignalSystem.for_network(scenario.network))
    sim = TrafficSimulation(scenario, entry_policy=policy)
    for _ in range(15):
        sim.step()

    # Use single intersection subproblem for fast, realistic integration test (N=4 qubits)
    valid_nodes = {"I1"}
    sub_network = scenario.network.model_copy(
        update={
            "nodes": tuple(n for n in scenario.network.nodes if n.node_id in valid_nodes),
            "edges": tuple(e for e in scenario.network.edges if e.source in valid_nodes and e.target in valid_nodes),
        }
    )

    qubo_config = SignalQuboConfig(horizon_intervals=2)
    qaoa_config = QAOAConfig(reps=1, shots=1024, seed=42, max_iterations=25)
    result = solve_signal_qubo_with_qaoa(
        network=sub_network,
        simulation_state=sim.state,
        qubo_config=qubo_config,
        qaoa_config=qaoa_config,
    )

    assert result.solver_name == "qaoa"
    assert result.backend_name == "qiskit_aer"
    assert result.num_qubits == 4  # 1 intersection * 2 phases * 2 intervals
    assert result.is_feasible is True
    assert result.decoded_schedule is not None
    assert len(result.decoded_schedule.decisions) == 2
    assert result.execution_time > 0.0
