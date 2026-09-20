"""Solver abstraction with explicit execution metadata and transparent fallback."""

import time
from typing import Any

import dimod

from app.domain.optimization import ExecutionClass, SolverMetadata


def solve_qubo(
    bqm: dimod.BinaryQuadraticModel,
    *,
    method: str = "neal",
    num_reads: int = 200,
) -> tuple[dict[str, int], float, SolverMetadata, bool, str | None]:
    """Solve BQM using requested solver method with fallback tracking.

    Returns:
        (best_sample, energy, solver_metadata, fallback_used, fallback_reason)
    """
    start_time = time.perf_counter()
    requested_method = method.lower()

    if bqm.num_variables == 0:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return (
            {},
            0.0,
            SolverMetadata(
                solver_name="empty",
                backend_name="none",
                execution_class=ExecutionClass.CLASSICAL,
                parameters={"num_variables": 0, "runtime_ms": elapsed_ms},
            ),
            False,
            None,
        )

    best_sample: dict[str, int] = {}
    energy: float = 0.0
    actual_solver = requested_method
    backend_name = "local"
    execution_class = ExecutionClass.CLASSICAL
    fallback_used = False
    fallback_reason: str | None = None
    sampler: Any = None

    if requested_method == "exact":
        actual_solver = "exact"
        backend_name = "dimod_exact"
        execution_class = ExecutionClass.CLASSICAL
        sampler = dimod.ExactSolver()
        sampleset = sampler.sample(bqm)
        best_sample = {str(k): int(v) for k, v in sampleset.first.sample.items()}
        energy = float(sampleset.first.energy)

    elif requested_method == "neal":
        try:
            import neal  # type: ignore[import-untyped, import-not-found, unused-ignore]

            sampler = neal.SimulatedAnnealingSampler()
            sampleset = sampler.sample(
                bqm,
                num_reads=num_reads,
                num_sweeps=1000,
                beta_range=[0.1, 10.0],
            )
            best_sample = {str(k): int(v) for k, v in sampleset.first.sample.items()}
            energy = float(sampleset.first.energy)
            actual_solver = "neal_sa"
            backend_name = "neal_sa"
            execution_class = ExecutionClass.CLASSICAL
        except Exception as exc:  # noqa: BLE001
            fallback_used = True
            fallback_reason = f"Neal SA execution unavailable ({exc})"
            actual_solver = "dimod_sa"
            backend_name = "dimod_simulated_annealing"
            execution_class = ExecutionClass.CLASSICAL_FALLBACK
            sampler = dimod.SimulatedAnnealingSampler()
            sampleset = sampler.sample(bqm, num_reads=num_reads)
            best_sample = {str(k): int(v) for k, v in sampleset.first.sample.items()}
            energy = float(sampleset.first.energy)

    elif requested_method == "tabu":
        try:
            import tabu  # type: ignore[import-not-found, unused-ignore]

            sampler = tabu.TabuSampler()
            sampleset = sampler.sample(bqm, num_reads=num_reads, timeout=1000)
            best_sample = {str(k): int(v) for k, v in sampleset.first.sample.items()}
            energy = float(sampleset.first.energy)
            actual_solver = "tabu"
            backend_name = "tabu_search"
            execution_class = ExecutionClass.CLASSICAL
        except Exception as exc:  # noqa: BLE001
            fallback_used = True
            fallback_reason = f"Tabu solver unavailable ({exc})"
            actual_solver = "dimod_sa"
            backend_name = "dimod_simulated_annealing"
            execution_class = ExecutionClass.CLASSICAL_FALLBACK
            sampler = dimod.SimulatedAnnealingSampler()
            sampleset = sampler.sample(bqm, num_reads=num_reads)
            best_sample = {str(k): int(v) for k, v in sampleset.first.sample.items()}
            energy = float(sampleset.first.energy)

    else:  # "sa" or unknown
        actual_solver = "dimod_sa"
        backend_name = "dimod_simulated_annealing"
        execution_class = ExecutionClass.CLASSICAL
        sampler = dimod.SimulatedAnnealingSampler()
        sampleset = sampler.sample(bqm, num_reads=num_reads)
        best_sample = {str(k): int(v) for k, v in sampleset.first.sample.items()}
        energy = float(sampleset.first.energy)

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    params: dict[str, Any] = {
        "requested_method": requested_method,
        "actual_method": actual_solver,
        "num_reads": num_reads,
        "num_variables": bqm.num_variables,
        "runtime_ms": elapsed_ms,
    }

    metadata = SolverMetadata(
        solver_name=actual_solver,
        backend_name=backend_name,
        execution_class=execution_class,
        parameters=params,
    )

    return best_sample, energy, metadata, fallback_used, fallback_reason
