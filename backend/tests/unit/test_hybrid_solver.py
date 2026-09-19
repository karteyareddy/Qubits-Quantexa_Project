"""Unit tests for HybridSignalOptimizer execution modes and fallback policies."""

from app.domain.signal import SignalPhase
from app.optimization.hybrid_models import HybridOptimizerConfig
from app.optimization.hybrid_solver import HybridSignalOptimizer
from app.quantum.config import QAOAConfig
from app.signals.qubo.config import SignalQuboConfig


def test_hybrid_optimizer_classical_reference_mode() -> None:
    var_names = ["x_I1_P0_T0", "x_I1_P1_T0"]
    var_map = {("I1", 0, 0): "x_I1_P0_T0", ("I1", 1, 0): "x_I1_P1_T0"}
    legal_phases = {"I1": (SignalPhase.EW_GREEN, SignalPhase.NS_GREEN)}

    Q = {
        ("x_I1_P0_T0", "x_I1_P0_T0"): -100.0,
        ("x_I1_P1_T0", "x_I1_P1_T0"): -100.0,
        ("x_I1_P0_T0", "x_I1_P1_T0"): 200.0,
    }
    offset = 100.0

    config = HybridOptimizerConfig(mode="classical_reference")
    optimizer = HybridSignalOptimizer(config)
    res = optimizer.optimize_qubo(Q, offset, var_names, var_map, legal_phases, 1)

    assert res.status == "success"
    assert res.mode == "classical_reference"
    assert res.solver_name == "classical_reference"
    assert res.backend_name == "classical_enumeration"
    assert res.is_feasible is True
    assert res.selected_energy == 0.0
    assert res.energy_gap == 0.0
    assert res.fallback_used is False


def test_hybrid_optimizer_hybrid_mode_with_qaoa() -> None:
    var_names = ["x_I1_P0_T0", "x_I1_P1_T0"]
    var_map = {("I1", 0, 0): "x_I1_P0_T0", ("I1", 1, 0): "x_I1_P1_T0"}
    legal_phases = {"I1": (SignalPhase.EW_GREEN, SignalPhase.NS_GREEN)}

    Q = {
        ("x_I1_P0_T0", "x_I1_P0_T0"): -100.0,
        ("x_I1_P1_T0", "x_I1_P1_T0"): -100.0,
        ("x_I1_P0_T0", "x_I1_P1_T0"): 200.0,
    }
    offset = 100.0

    q_cfg = SignalQuboConfig(horizon_intervals=1)
    qaoa_cfg = QAOAConfig(reps=1, shots=512, seed=42, max_iterations=20)
    config = HybridOptimizerConfig(
        mode="hybrid",
        candidate_count=5,
        enable_refinement=True,
        qubo_config=q_cfg,
        qaoa_config=qaoa_cfg,
    )

    optimizer = HybridSignalOptimizer(config)
    res = optimizer.optimize_qubo(Q, offset, var_names, var_map, legal_phases, 1)

    assert res.mode == "hybrid"
    assert res.solver_name in ("hybrid_qaoa", "classical_reference")
    assert res.is_feasible is True
    assert res.selected_schedule is not None
    assert len(res.candidates) > 0
    assert res.energy_gap is not None
    assert abs(res.selected_energy - 0.0) < 1e-6


def test_default_live_qubo_fits_configured_aer_limit() -> None:
    config = HybridOptimizerConfig()
    assert config.qubo_config.horizon_intervals == 1


def test_oversized_qubo_uses_controlled_fallback_before_aer() -> None:
    intersections = [f"I{index}" for index in range(16)]
    variable_names = [
        f"x_{intersection}_P{phase}_T0"
        for intersection in intersections
        for phase in range(2)
    ]
    variable_map = {
        (intersection, phase, 0): f"x_{intersection}_P{phase}_T0"
        for intersection in intersections
        for phase in range(2)
    }
    legal_phases = {
        intersection: (SignalPhase.EW_GREEN, SignalPhase.NS_GREEN)
        for intersection in intersections
    }
    qubo = {(name, name): -1.0 for name in variable_names}

    result = HybridSignalOptimizer().optimize_qubo(
        qubo,
        0.0,
        variable_names,
        variable_map,
        legal_phases,
        1,
    )

    assert result.fallback_used is True
    assert result.fallback_reason is not None
    assert "requires 32 qubits" in result.fallback_reason
    assert "configured Aer limit of 30" in result.fallback_reason
