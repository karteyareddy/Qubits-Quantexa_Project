"""Signal preemption controller for applying emergency green corridors."""

from app.adaptive.controller import AdaptiveSignalPolicy
from app.domain.signal import SignalPhase
from app.emergency.models import CorridorStatus, EmergencyCorridor
from app.signals.policy import SignalSystem


class EmergencyCorridorController:
    """Controls emergency signal preemption over adaptive/fixed-time signal systems."""

    @staticmethod
    def get_intersection_override(
        corridor: EmergencyCorridor,
        intersection_id: str,
        simulation_time: float,
    ) -> SignalPhase | None:
        """Return required green phase override if simulation_time is within a reserved green window."""
        if corridor.status != CorridorStatus.ACTIVE:
            return None

        for res in corridor.intersections:
            if (
                res.intersection_id == intersection_id
                and res.green_window_start <= simulation_time + 1e-6 <= res.green_window_end + 1e-6
            ):
                return res.required_phase
        return None

    @classmethod
    def apply_corridor_overrides(
        cls,
        active_corridors: list[EmergencyCorridor],
        signal_system: SignalSystem,
        adaptive_policy: AdaptiveSignalPolicy | None,
        simulation_time: float,
    ) -> dict[str, SignalPhase]:
        """Apply active emergency corridor green window overrides to controlled intersections."""
        overrides: dict[str, SignalPhase] = {}

        for corridor in active_corridors:
            if corridor.status != CorridorStatus.ACTIVE:
                continue

            for res in corridor.intersections:
                if res.green_window_start <= simulation_time + 1e-6 <= res.green_window_end + 1e-6:
                    overrides[res.intersection_id] = res.required_phase

        if adaptive_policy is not None:
            if overrides:
                adaptive_policy.set_preemption_overrides(overrides)
            else:
                adaptive_policy.clear_preemption_overrides()

        return overrides
