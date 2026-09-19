"""Configuration for QAOA Quantum Solver."""

from pydantic import Field

from app.domain.base import DomainModel


class QAOAConfig(DomainModel):
    """Configuration options for QAOA quantum simulation solver."""

    reps: int = Field(default=1, ge=1, le=5, description="QAOA circuit depth (number of layers p)")
    shots: int = Field(default=1024, ge=1, le=10000, description="Number of measurement shots per circuit execution")
    seed: int = Field(default=42, description="Random seed for reproducible Aer simulation and classical optimization")
    optimizer_name: str = Field(default="COBYLA", description="Classical optimizer algorithm name (e.g. COBYLA, SPSA)")
    max_iterations: int = Field(default=40, ge=1, le=500, description="Maximum iterations for classical parameter optimizer")
    backend_name: str = Field(default="qiskit_aer", description="Quantum execution backend identifier")
    simulator_mode: str = Field(default="aer_simulator", description="Qiskit Aer simulator mode")
    initial_point_strategy: str = Field(
        default="random", description="Strategy for initial gamma/beta parameters ('random', 'zero', 'custom')"
    )
    custom_initial_point: tuple[float, ...] | None = Field(
        default=None, description="Custom initial parameters if strategy is 'custom'"
    )
