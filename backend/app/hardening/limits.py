"""Platform resource limits and safety thresholds."""

from pydantic import Field

from app.domain.base import DomainModel


class PlatformResourceLimits(DomainModel):
    """Configurable safety resource bounds for simulation and quantum optimization."""

    max_simulation_duration_seconds: float = Field(
        default=3600.0, ge=10.0, le=86400.0, description="Maximum allowed simulation duration"
    )
    max_vehicles_per_simulation: int = Field(
        default=500, ge=1, le=5000, description="Maximum total spawned vehicles allowed"
    )
    max_qubo_variables: int = Field(
        default=100, ge=1, le=500, description="Maximum allowed QUBO binary variables"
    )
    max_qaoa_qubits: int = Field(
        default=30, ge=1, le=30, description="Maximum qubits supported by Aer quantum simulator"
    )
    max_qaoa_shots: int = Field(
        default=10000, ge=100, le=100000, description="Maximum quantum circuit sampling shots"
    )
    max_benchmark_repetitions: int = Field(
        default=20, ge=1, le=100, description="Maximum repeated benchmark trials"
    )
    max_event_payload_size_bytes: int = Field(
        default=10000, ge=100, le=100000, description="Maximum allowed event payload size"
    )

    def validate_simulation_duration(self, duration_seconds: float) -> float:
        if duration_seconds <= 0.0:
            raise ValueError("Simulation duration must be strictly positive.")
        if duration_seconds > self.max_simulation_duration_seconds:
            raise ValueError(
                f"Simulation duration {duration_seconds}s exceeds platform limit of "
                f"{self.max_simulation_duration_seconds}s."
            )
        return duration_seconds

    def validate_vehicle_count(self, count: int) -> int:
        if count <= 0:
            raise ValueError("Vehicle count must be strictly positive.")
        if count > self.max_vehicles_per_simulation:
            raise ValueError(
                f"Vehicle count {count} exceeds platform limit of {self.max_vehicles_per_simulation}."
            )
        return count

    def validate_qubo_variable_count(self, num_vars: int) -> int:
        if num_vars <= 0:
            raise ValueError("QUBO variable count must be positive.")
        if num_vars > self.max_qubo_variables:
            raise ValueError(
                f"QUBO variable count {num_vars} exceeds platform safety threshold of {self.max_qubo_variables}."
            )
        return num_vars


DEFAULT_PLATFORM_LIMITS = PlatformResourceLimits()
