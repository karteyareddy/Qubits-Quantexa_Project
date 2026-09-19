"""QAOA Quantum Solver for Stage 8 Signal-Control QUBO."""

import time
from collections.abc import Mapping, Sequence

import numpy as np
from scipy.optimize import minimize  # type: ignore[import-untyped]

from app.domain.signal import SignalPhase
from app.domain.signal_qubo import SignalSchedule
from app.quantum.backend import execute_qaoa_circuit
from app.quantum.circuit import build_qaoa_circuit
from app.quantum.config import QAOAConfig
from app.quantum.ising import qubo_to_ising
from app.quantum.models import QAOAResult
from app.signals.qubo.decoder import decode_signal_qubo_solution
from app.signals.qubo.evaluator import evaluate_qubo_energy


def qiskit_bitstring_to_qubo_assignment(
    qiskit_bitstring: str,
    variable_names: Sequence[str],
) -> dict[str, int]:
    """Convert Qiskit big-endian measurement string to QUBO variable assignment map.

    In Qiskit measurement output strings (e.g. '10'):
    - Rightmost character (index -1) represents qubit 0 / variable_names[0].
    - Leftmost character (index 0) represents qubit N-1 / variable_names[N-1].
    """
    assignment: dict[str, int] = {}
    for i, var_name in enumerate(variable_names):
        bit_char = qiskit_bitstring[-(i + 1)]
        assignment[var_name] = 1 if bit_char == "1" else 0
    return assignment


def qiskit_bitstring_to_standard_string(qiskit_bitstring: str) -> str:
    """Reverse Qiskit bitstring so index i corresponds to qubit i / variable i."""
    return qiskit_bitstring[::-1]


def standard_string_to_qiskit_bitstring(standard_string: str) -> str:
    """Convert standard bitstring (index i = qubit i) to Qiskit bitstring representation."""
    return standard_string[::-1]


class QAOASolver:
    """Quantum Approximate Optimization Algorithm solver for Signal-Control QUBO."""

    def __init__(self, config: QAOAConfig | None = None) -> None:
        self.config = config or QAOAConfig()

    def solve_qubo(
        self,
        Q: dict[tuple[str, str], float],
        constant_offset: float,
        variable_names: Sequence[str],
        variable_map: dict[tuple[str, int, int], str],
        intersection_legal_phases: Mapping[str, Sequence[SignalPhase]] | None = None,
        horizon_intervals: int = 2,
    ) -> QAOAResult:
        """Solve QUBO using QAOA circuit execution and classical parameter optimization."""
        start_time = time.perf_counter()
        num_qubits = len(variable_names)
        reps = self.config.reps

        # 1. Convert QUBO to Ising formulation
        h_coeffs, J_coeffs, _c_ising = qubo_to_ising(Q, constant_offset, variable_names)

        # Track optimization trajectory
        energy_history: list[float] = []
        param_history_list: list[tuple[float, ...]] = []

        # Objective function for classical parameter optimization
        def cost_function(params: np.ndarray) -> float:
            gammas = [float(x) for x in params[:reps]]
            betas = [float(x) for x in params[reps:]]
            param_history_list.append(tuple(gammas + betas))

            circuit = build_qaoa_circuit(num_qubits, h_coeffs, J_coeffs, gammas, betas)
            counts = execute_qaoa_circuit(circuit, self.config)

            total_shots = sum(counts.values())
            expected_energy = 0.0

            for qiskit_str, count in counts.items():
                assignment = qiskit_bitstring_to_qubo_assignment(qiskit_str, variable_names)
                e_val = evaluate_qubo_energy(Q, assignment, constant_offset)
                expected_energy += (count / total_shots) * e_val

            energy_history.append(expected_energy)
            return expected_energy

        # 2. Initial parameters setup
        rng = np.random.default_rng(self.config.seed)
        if self.config.initial_point_strategy == "custom" and self.config.custom_initial_point:
            init_params = np.array(self.config.custom_initial_point, dtype=float)
        elif self.config.initial_point_strategy == "zero":
            init_params = np.zeros(2 * reps, dtype=float)
        else:
            # Standard heuristic range: gammas in [0, pi], betas in [0, pi/2]
            init_gammas = rng.uniform(0.0, np.pi, reps)
            init_betas = rng.uniform(0.0, np.pi / 2.0, reps)
            init_params = np.concatenate([init_gammas, init_betas])

        # 3. Classical Optimization Loop
        opt_res = minimize(
            cost_function,
            init_params,
            method=self.config.optimizer_name,
            options={"maxiter": self.config.max_iterations},
        )

        opt_gammas = tuple(float(x) for x in opt_res.x[:reps])
        opt_betas = tuple(float(x) for x in opt_res.x[reps:])

        # 4. Final Optimal Sampling Run
        final_circuit = build_qaoa_circuit(num_qubits, h_coeffs, J_coeffs, opt_gammas, opt_betas)
        final_counts = execute_qaoa_circuit(final_circuit, self.config)

        # 5. Evaluate all sampled bitstrings and find best feasible solution
        best_bitstring = ""
        best_energy = float("inf")
        best_schedule: SignalSchedule | None = None
        best_feasible = False

        fallback_bitstring = ""
        fallback_energy = float("inf")

        # Set default legal phases if not provided
        legal_phases_dict: dict[str, Sequence[SignalPhase]] = {}
        if intersection_legal_phases is None:
            intersections = sorted({var.split("_")[1] for var in variable_names if var.startswith("x_")})
            legal_phases_dict = {
                i_id: (SignalPhase.EW_GREEN, SignalPhase.NS_GREEN) for i_id in intersections
            }
        else:
            legal_phases_dict = dict(intersection_legal_phases)

        for qiskit_str in final_counts:
            assignment = qiskit_bitstring_to_qubo_assignment(qiskit_str, variable_names)
            energy = evaluate_qubo_energy(Q, assignment, constant_offset)
            std_bitstring = qiskit_bitstring_to_standard_string(qiskit_str)

            if energy < fallback_energy:
                fallback_energy = energy
                fallback_bitstring = std_bitstring

            sched, feasibility, _bit = decode_signal_qubo_solution(
                assignment=assignment,
                variable_map=variable_map,
                variable_names=variable_names,
                intersection_legal_phases=legal_phases_dict,
                horizon_intervals=horizon_intervals,
            )

            if feasibility.feasible and energy < best_energy:
                best_energy = energy
                best_bitstring = std_bitstring
                best_schedule = sched
                best_feasible = True

        # If no sampled state was feasible, pick lowest energy state overall
        if not best_feasible or not best_bitstring:
            best_bitstring = fallback_bitstring
            best_energy = fallback_energy
            best_feasible = False

        exec_time = time.perf_counter() - start_time
        n_fev = int(opt_res.nfev) if hasattr(opt_res, "nfev") else len(energy_history)

        return QAOAResult(
            best_bitstring=best_bitstring,
            best_energy=best_energy,
            objective_value=best_energy,
            is_feasible=best_feasible,
            decoded_schedule=best_schedule,
            num_qubits=num_qubits,
            reps=reps,
            shots=self.config.shots,
            backend_name=self.config.backend_name,
            solver_name="qaoa",
            optimization_iterations=n_fev,
            execution_time=exec_time,
            seed=self.config.seed,
            measurement_counts=final_counts,
            optimal_gammas=opt_gammas,
            optimal_betas=opt_betas,
            energy_history=tuple(energy_history),
            parameter_history=tuple(param_history_list),
        )
