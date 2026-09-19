"""Emergency corridor planning and validation."""

from app.domain.network import Network
from app.domain.vehicle import Vehicle
from app.emergency.models import (
    CorridorStatus,
    EmergencyCorridor,
    EmergencyCorridorConfig,
)
from app.emergency.predictor import EmergencyETAPredictor
from app.emergency.route import EmergencyRouteError, EmergencyRouteExtractor


class EmergencyCorridorPlanner:
    """Plans, validates, and builds EmergencyCorridor instances."""

    @staticmethod
    def plan_corridor(
        vehicle: Vehicle,
        network: Network,
        current_time: float,
        config: EmergencyCorridorConfig | None = None,
        corridor_id: str | None = None,
    ) -> EmergencyCorridor:
        """Construct a validated time-aware EmergencyCorridor for an emergency vehicle."""
        cfg = config or EmergencyCorridorConfig()
        cid = corridor_id or f"corridor_{vehicle.vehicle_id}_{int(current_time)}"

        try:
            route = EmergencyRouteExtractor.extract_and_validate_route(vehicle, network)
            sequence = EmergencyRouteExtractor.extract_intersection_sequence(network, route)

            if not sequence:
                raise EmergencyRouteError(
                    f"Emergency route for vehicle '{vehicle.vehicle_id}' contains no signalized intersections."
                )

            reservations = EmergencyETAPredictor.predict_corridor_reservations(
                vehicle=vehicle,
                network=network,
                sequence=sequence,
                current_time=current_time,
                config=cfg,
            )

            return EmergencyCorridor(
                corridor_id=cid,
                vehicle_id=vehicle.vehicle_id,
                route=route,
                intersections=tuple(reservations),
                status=CorridorStatus.PLANNED,
                created_at_seconds=current_time,
            )
        except (EmergencyRouteError, ValueError, RuntimeError) as exc:
            # Construct failed corridor for explicit status logging
            dummy_route = vehicle.route or EmergencyRouteExtractor.extract_and_validate_route(vehicle, network)
            return EmergencyCorridor(
                corridor_id=cid,
                vehicle_id=vehicle.vehicle_id,
                route=dummy_route,
                intersections=(),
                status=CorridorStatus.FAILED,
                created_at_seconds=current_time,
                failure_reason=str(exc),
            )
