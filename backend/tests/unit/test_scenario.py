"""Tests for the serializable scenario contract."""

import pytest
from app.domain.network import Network
from app.domain.scenario import Scenario
from app.domain.signal import SignalPhase, SignalState
from app.domain.vehicle import Vehicle, VehicleType
from pydantic import ValidationError


def test_scenario_preserves_seed_and_serializes_nested_models(sample_network: Network) -> None:
    scenario = Scenario(
        scenario_id="scenario-1",
        seed=42,
        duration_seconds=300.0,
        network=sample_network,
        vehicles=(
            Vehicle(
                vehicle_id="vehicle-1",
                vehicle_type=VehicleType.REGULAR,
                origin="I1",
                destination="I2",
            ),
        ),
        signals=(
            SignalState(
                intersection_id="I1",
                current_phase=SignalPhase.NS_GREEN,
                phase_started_at_seconds=0.0,
                remaining_time_seconds=20.0,
                legal_phases=tuple(SignalPhase),
            ),
        ),
    )

    serialized = scenario.model_dump(mode="json")

    assert scenario.seed == 42
    assert serialized["network"]["nodes"][0]["node_id"] == "I1"
    assert serialized["signals"][0]["current_phase"] == "NS_GREEN"


def test_scenario_rejects_unknown_vehicle_endpoint(sample_network: Network) -> None:
    with pytest.raises(ValidationError, match="endpoints"):
        Scenario(
            scenario_id="scenario-1",
            seed=42,
            duration_seconds=300.0,
            network=sample_network,
            vehicles=(
                Vehicle(
                    vehicle_id="vehicle-1",
                    vehicle_type=VehicleType.REGULAR,
                    origin="missing",
                    destination="I2",
                ),
            ),
        )
