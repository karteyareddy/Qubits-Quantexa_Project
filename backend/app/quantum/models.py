"""QAOA Execution Result contracts."""

from pydantic import Field

from app.domain.base import DomainModel
from app.domain.signal_qubo import SignalSchedule


class QAOAResult(DomainModel):
    """Result data structure returned by the QAOA signal optimization solver."""

    best_bitstring: str = Field(description="Binary bitstring corresponding to lowest-energy valid/best assignment")
    best_energy: float = Field(description="Exact Stage 8 QUBO energy value for the best bitstring")
    objective_value: float = Field(description="Objective cost function value (energy - constant constraint offsets)")
    is_feasible: bool = Field(description="Whether the best solution satisfies signal phase constraints")
    decoded_schedule: SignalSchedule | None = Field(default=None, description="Decoded signal schedule if feasible")
    num_qubits: int = Field(description="Number of qubits in the QAOA circuit (equals QUBO variable count)")
    reps: int = Field(description="QAOA circuit depth p")
    shots: int = Field(description="Number of shots per execution")
    backend_name: str = Field(default="qiskit_aer", description="Quantum simulator / backend identifier")
    solver_name: str = Field(default="qaoa", description="Explicit solver identity")
    optimization_iterations: int = Field(description="Number of iterations executed by classical optimizer")
    execution_time: float = Field(description="Wall-clock execution time in seconds")
    seed: int = Field(description="Random seed used for quantum execution")
    measurement_counts: dict[str, int] = Field(default_factory=dict, description="Bitstring measurement frequency map")
    optimal_gammas: tuple[float, ...] = Field(default_factory=tuple, description="Optimized cost layer angles gamma")
    optimal_betas: tuple[float, ...] = Field(default_factory=tuple, description="Optimized mixer layer angles beta")
    energy_history: tuple[float, ...] = Field(default_factory=tuple, description="Expected energy value per optimizer iteration")
    parameter_history: tuple[tuple[float, ...], ...] = Field(
        default_factory=tuple, description="Parameter vectors (gammas + betas) per optimizer iteration"
    )
