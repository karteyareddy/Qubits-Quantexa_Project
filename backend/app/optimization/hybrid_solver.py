"""Hybrid Quantum-Classical Signal Optimizer orchestrator."""

import time
from collections.abc import Mapping, Sequence

from app.domain.network import Network
from app.domain.signal import SignalPhase
from app.optimization.hybrid_candidates import extract_candidates
from app.optimization.hybrid_models import (
    CandidateSolution,
    HybridOptimizationResult,
    HybridOptimizerConfig,
)
from app.optimization.hybrid_refinement import refine_candidate_solution
from app.quantum.qaoa import (
    QAOASolver,
    qiskit_bitstring_to_qubo_assignment,
    standard_string_to_qiskit_bitstring,
)
from app.signals.qubo.builder import SignalQuboBuilder
from app.signals.qubo.decoder import decode_signal_qubo_solution
from app.signals.qubo.evaluator import evaluate_qubo_energy
from app.signals.qubo.reference_solver import solve_signal_qubo_brute_force
from app.simulation.models import SimulationState


class HybridSignalOptimizer:
    """Orchestrates Stage 8 QUBO construction, Stage 9 QAOA, top-K candidate extraction,

    local classical refinement, and classical exact reference comparison.
    """

    def __init__(self, config: HybridOptimizerConfig | None = None) -> None:
        self.config = config or HybridOptimizerConfig()

    def optimize_qubo(
        self,
        Q: dict[tuple[str, str], float],
        constant_offset: float,
        variable_names: Sequence[str],
        variable_map: dict[tuple[str, int, int], str],
        intersection_legal_phases: Mapping[str, Sequence[SignalPhase]],
        horizon_intervals: int = 2,
    ) -> HybridOptimizationResult:
        """Execute hybrid optimization pipeline on pre-constructed QUBO matrix."""
        start_time = time.perf_counter()
        cfg = self.config
        num_vars = len(variable_names)

        qaoa_time = 0.0
        classical_time = 0.0
        refinement_time = 0.0

        qaoa_res = None
        candidates: list[CandidateSolution] = []
        selected_cand: CandidateSolution

        # 1. Handle classical_reference mode directly
        if cfg.mode == "classical_reference":
            c_start = time.perf_counter()
            best_sample, exact_energy, exact_bitstring = solve_signal_qubo_brute_force(
                Q, variable_names, constant_offset
            )
            classical_time = time.perf_counter() - c_start

            sched, feasibility, _bit = decode_signal_qubo_solution(
                assignment=best_sample,
                variable_map=variable_map,
                variable_names=variable_names,
                intersection_legal_phases=intersection_legal_phases,
                horizon_intervals=horizon_intervals,
            )

            selected_cand = CandidateSolution(
                bitstring=exact_bitstring,
                probability=1.0,
                qubo_energy=exact_energy,
                is_feasible=feasibility.feasible,
                decoded_schedule=sched,
            )

            total_time = time.perf_counter() - start_time
            return HybridOptimizationResult(
                status="success",
                mode="classical_reference",
                solver_name="classical_reference",
                backend_name="classical_enumeration",
                qaoa_result=None,
                candidates=(selected_cand,),
                selected_solution=selected_cand,
                selected_energy=exact_energy,
                selected_schedule=sched,
                classical_reference_energy=exact_energy,
                energy_gap=0.0,
                is_feasible=feasibility.feasible,
                optimization_time=total_time,
                qaoa_time=0.0,
                classical_time=classical_time,
                refinement_time=0.0,
                fallback_used=False,
                fallback_reason=None,
            )

        # 2. Run QAOA Optimization
        q_start = time.perf_counter()
        qaoa_solver = QAOASolver(config=cfg.qaoa_config)
        qaoa_failed = False
        qaoa_fail_msg = ""
        qaoa_time = 0.0

        if num_vars > cfg.qaoa_config.max_qubits:
            qaoa_failed = True
            qaoa_fail_msg = (
                f"QUBO requires {num_vars} qubits, exceeding the configured Aer limit of "
                f"{cfg.qaoa_config.max_qubits}"
            )
            feasible_candidates = []
        else:
            try:
                qaoa_res = qaoa_solver.solve_qubo(
                    Q=Q,
                    constant_offset=constant_offset,
                    variable_names=variable_names,
                    variable_map=variable_map,
                    intersection_legal_phases=intersection_legal_phases,
                    horizon_intervals=horizon_intervals,
                )
                qaoa_time = time.perf_counter() - q_start

                # 3. Extract top-K candidates from QAOA measurement distribution
                candidates = extract_candidates(
                    measurement_counts=qaoa_res.measurement_counts,
                    Q=Q,
                    constant_offset=constant_offset,
                    variable_names=variable_names,
                    variable_map=variable_map,
                    intersection_legal_phases=intersection_legal_phases,
                    horizon_intervals=horizon_intervals,
                    top_k=cfg.candidate_count,
                )
                feasible_candidates = [c for c in candidates if c.is_feasible]
            except Exception as exc:  # noqa: BLE001
                qaoa_failed = True
                qaoa_fail_msg = str(exc)
                feasible_candidates = []

        fallback_used = False
        fallback_reason = None

        # 4. Handle Case: No feasible candidate sampled by QAOA or QAOA failed
        if not feasible_candidates or qaoa_failed:
            if cfg.allow_classical_fallback:
                fallback_used = True
                fallback_reason = (
                    f"QAOA solver error: {qaoa_fail_msg}"
                    if qaoa_failed
                    else "No feasible QAOA candidate sampled from measurement distribution"
                )
                c_start = time.perf_counter()
                if num_vars <= 20:
                    best_sample, exact_energy, exact_bitstring = solve_signal_qubo_brute_force(
                        Q, variable_names, constant_offset
                    )
                else:
                    # Construct default legal assignment for N > 20
                    best_sample = {}
                    bit_chars = []
                    for name in variable_names:
                        parts = name.split("_")
                        if len(parts) >= 4 and parts[2] == "P0":
                            best_sample[name] = 1
                            bit_chars.append("1")
                        else:
                            best_sample[name] = 0
                            bit_chars.append("0")
                    exact_energy = evaluate_qubo_energy(Q, best_sample, constant_offset)
                    exact_bitstring = "".join(bit_chars)

                classical_time += time.perf_counter() - c_start

                sched, feasibility, _bit = decode_signal_qubo_solution(
                    assignment=best_sample,
                    variable_map=variable_map,
                    variable_names=variable_names,
                    intersection_legal_phases=intersection_legal_phases,
                    horizon_intervals=horizon_intervals,
                )

                selected_cand = CandidateSolution(
                    bitstring=exact_bitstring,
                    probability=1.0,
                    qubo_energy=exact_energy,
                    is_feasible=feasibility.feasible,
                    decoded_schedule=sched,
                )
            else:
                # If fallback disallowed or problem too large, select best infeasible candidate
                selected_cand = candidates[0] if candidates else CandidateSolution(
                    bitstring="0" * num_vars,
                    probability=0.0,
                    qubo_energy=float("inf"),
                    is_feasible=False,
                    decoded_schedule=None,
                )
        else:
            # Pick lowest-energy feasible QAOA candidate
            selected_cand = feasible_candidates[0]

            # 5. Optional Classical Local Refinement
            if cfg.mode == "hybrid" and cfg.enable_refinement and selected_cand.is_feasible:
                r_start = time.perf_counter()
                selected_cand = refine_candidate_solution(
                    candidate=selected_cand,
                    Q=Q,
                    constant_offset=constant_offset,
                    variable_names=variable_names,
                    variable_map=variable_map,
                    intersection_legal_phases=intersection_legal_phases,
                    horizon_intervals=horizon_intervals,
                    max_steps=cfg.max_refinement_steps,
                )
                refinement_time = time.perf_counter() - r_start

        # 6. Verify exact energy matching against Stage 8 evaluator
        q_str = standard_string_to_qiskit_bitstring(selected_cand.bitstring)
        sel_assign = qiskit_bitstring_to_qubo_assignment(q_str, variable_names)
        eval_energy = evaluate_qubo_energy(Q, sel_assign, constant_offset)

        # 7. Optional Classical Reference Gap Computation
        exact_ref_energy: float | None = None
        energy_gap: float | None = None
        if cfg.evaluate_classical_reference_gap and num_vars <= 20:
            c_start = time.perf_counter()
            _sample, exact_ref_energy, _bit = solve_signal_qubo_brute_force(
                Q, variable_names, constant_offset
            )
            classical_time += time.perf_counter() - c_start
            energy_gap = eval_energy - exact_ref_energy

        # 8. Determine final solver and backend labels
        if fallback_used:
            solver_label = "classical_reference"
            backend_label = "classical_enumeration"
            status_label = "fallback"
        elif cfg.mode == "hybrid":
            solver_label = "hybrid_qaoa"
            backend_label = cfg.qaoa_config.backend_name
            status_label = "success" if selected_cand.is_feasible else "failed"
        else:
            solver_label = "qaoa"
            backend_label = cfg.qaoa_config.backend_name
            status_label = "success" if selected_cand.is_feasible else "failed"

        total_time = time.perf_counter() - start_time

        return HybridOptimizationResult(
            status=status_label,
            mode=cfg.mode,
            solver_name=solver_label,
            backend_name=backend_label,
            qaoa_result=qaoa_res,
            candidates=tuple(candidates),
            selected_solution=selected_cand,
            selected_energy=eval_energy,
            selected_schedule=selected_cand.decoded_schedule,
            classical_reference_energy=exact_ref_energy,
            energy_gap=energy_gap,
            is_feasible=selected_cand.is_feasible,
            optimization_time=total_time,
            qaoa_time=qaoa_time,
            classical_time=classical_time,
            refinement_time=refinement_time,
            fallback_used=fallback_used,
            fallback_reason=fallback_reason,
        )

    def optimize(
        self,
        network: Network,
        state: SimulationState,
        *,
        current_phases: dict[str, SignalPhase] | None = None,
    ) -> HybridOptimizationResult:
        """Build Stage 8 QUBO from traffic state snapshot and execute hybrid optimization."""
        builder = SignalQuboBuilder(config=self.config.qubo_config)
        Q, offset, var_names, var_map = builder.build_qubo(
            network, state, current_phases=current_phases
        )

        intersections = sorted(node.node_id for node in network.nodes if node.is_intersection)
        legal_phases: dict[str, Sequence[SignalPhase]] = {
            i_id: (SignalPhase.EW_GREEN, SignalPhase.NS_GREEN)
            for i_id in intersections
        }

        return self.optimize_qubo(
            Q=Q,
            constant_offset=offset,
            variable_names=var_names,
            variable_map=var_map,
            intersection_legal_phases=legal_phases,
            horizon_intervals=self.config.qubo_config.horizon_intervals,
        )
