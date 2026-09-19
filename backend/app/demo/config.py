"""Configuration parameters for deterministic hackathon demonstration."""

from pydantic import Field

from app.domain.base import DomainModel


class DemoConfig(DomainModel):
    """Preset configuration parameters for live demo execution."""

    scenario_id: str = Field(default="demo-scenario", description="ID of preset demo scenario")
    seed: int = Field(default=42, description="Fixed seed for deterministic traffic and events")
    duration_seconds: float = Field(
        default=60.0, ge=10.0, le=300.0, description="Duration of demo simulation"
    )
    control_interval_seconds: float = Field(
        default=5.0, ge=1.0, le=30.0, description="Adaptive optimization interval"
    )
    enable_qaoa: bool = Field(
        default=True, description="Enable hybrid QAOA optimization during demo"
    )
    enable_events: bool = Field(
        default=True, description="Enable dynamic event injection during demo"
    )
    enable_emergency_corridor: bool = Field(
        default=True, description="Enable Emergency Green Corridor during demo"
    )


DEFAULT_DEMO_CONFIG = DemoConfig()
