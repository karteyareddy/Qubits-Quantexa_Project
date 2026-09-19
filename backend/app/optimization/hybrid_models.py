"""Typed domain models for Hybrid Quantum-Classical Signal Optimization."""

from pydantic import Field

from app.domain.base import DomainModel
from app.domain.signal_qubo import SignalSchedule
from app.quantum.config import QAOAConfig
from app.quantum.models import QAOAResult
from app.signals.qubo.config import SignalQuboConfig


class CandidateSolution(DomainModel):
    """Single candidate binary solution evaluated from measurement string or classical search."""

    bitstring: str = Field(description="Standard binary string representation (index i = qubit i)")
    probability: float = Field(ge=0.0, le=1.0, description="Measured sampling probability from quantum execution")
    qubo_energy: float = Field(description="Exact Stage 8 QUBO energy for this bitstring")
    is_feasible: bool = Field(description="Whether the bitstring satisfies exactly-one-phase signal constraints")
    decoded_schedule: SignalSchedule | None = Field(default=None, description="Decoded signal schedule if feasible")


class HybridOptimizerConfig(DomainModel):
    """Configuration options for the Hybrid Quantum-Classical Signal Optimizer."""

    mode: str = Field(
        default="hybrid",
        description="Optimization execution mode: 'hybrid', 'qaoa_only', or 'classical_reference'",
    )
    candidate_count: int = Field(default=5, ge=1, le=50, description="Top-K unique candidates to extract and evaluate")
    enable_refinement: bool = Field(default=True, description="Whether to apply classical local 1-bit flip refinement")
    max_refinement_steps: int = Field(default=50, ge=1, le=500, description="Maximum iterations for local refinement")
    allow_classical_fallback: bool = Field(
        default=True, description="Whether to fall back to classical reference solver if QAOA yields no feasible candidate"
    )
    evaluate_classical_reference_gap: bool = Field(
        default=True, description="Whether to compute energy gap against classical exact baseline"
    )
    qubo_config: SignalQuboConfig = Field(default_factory=SignalQuboConfig)
    qaoa_config: QAOAConfig = Field(default_factory=QAOAConfig)


class HybridOptimizationResult(DomainModel):
    """Complete result returned by the Hybrid Signal Optimizer."""

    status: str = Field(description="Execution status: 'success', 'fallback', or 'failed'")
    mode: str = Field(description="Configured optimization mode used")
    solver_name: str = Field(description="Explicit solver identity ('qaoa', 'hybrid_qaoa', 'classical_reference')")
    backend_name: str = Field(description="Execution backend identifier ('qiskit_aer', 'classical_enumeration')")
    qaoa_result: QAOAResult | None = Field(default=None, description="Raw Stage 9 QAOA result if executed")
    candidates: tuple[CandidateSolution, ...] = Field(default_factory=tuple, description="Extracted top-K unique candidates")
    selected_solution: CandidateSolution = Field(description="Final selected candidate solution")
    selected_energy: float = Field(description="Exact Stage 8 QUBO energy of selected solution")
    selected_schedule: SignalSchedule | None = Field(default=None, description="Final decoded signal schedule")
    classical_reference_energy: float | None = Field(default=None, description="Exact classical ground-truth energy if computed")
    energy_gap: float | None = Field(default=None, description="Energy difference (selected_energy - classical_reference_energy)")
    is_feasible: bool = Field(description="Whether final selected solution is feasible")
    optimization_time: float = Field(description="Total wall-clock optimization time in seconds")
    qaoa_time: float = Field(default=0.0, description="QAOA execution time in seconds")
    classical_time: float = Field(default=0.0, description="Classical solver time in seconds")
    refinement_time: float = Field(default=0.0, description="Local refinement time in seconds")
    fallback_used: bool = Field(default=False, description="Whether classical fallback solver was used")
    fallback_reason: str | None = Field(default=None, description="Reason for classical fallback if applicable")
