"""Deterministic scheduled and seeded vehicle arrival generation."""

from random import Random

from app.domain.network import Network
from app.domain.vehicle import EmergencySubtype, Vehicle, VehicleType
from app.routing.routes import shortest_route
from app.simulation.models import ScheduledArrival

_EMERGENCY_SUBTYPES = tuple(EmergencySubtype)


def scheduled_arrival(
    network: Network,
    *,
    vehicle_id: str,
    origin: str,
    destination: str,
    arrival_time_seconds: float,
    emergency_subtype: EmergencySubtype | None = None,
    priority_weight: int | None = None,
) -> ScheduledArrival:
    """Create one explicitly scheduled vehicle with a deterministic shortest route."""
    is_emergency = emergency_subtype is not None
    route = shortest_route(network, origin, destination)
    vehicle = Vehicle(
        vehicle_id=vehicle_id,
        vehicle_type=VehicleType.EMERGENCY if is_emergency else VehicleType.REGULAR,
        origin=origin,
        destination=destination,
        route=route,
        candidate_routes=(route,),
        is_emergency=is_emergency,
        emergency_subtype=emergency_subtype,
        priority_weight=priority_weight or (10 if is_emergency else 1),
        arrival_time_seconds=arrival_time_seconds,
    )
    return ScheduledArrival(arrival_time_seconds=arrival_time_seconds, vehicle=vehicle)


def generate_seeded_arrivals(
    network: Network,
    *,
    count: int,
    seed: int,
    horizon_seconds: int,
    emergency_ratio: float = 0.0,
) -> tuple[ScheduledArrival, ...]:
    """Generate reproducible demand without touching global random state."""
    if count < 0:
        raise ValueError("arrival count cannot be negative")
    if horizon_seconds < 0:
        raise ValueError("arrival horizon cannot be negative")
    if not 0.0 <= emergency_ratio <= 1.0:
        raise ValueError("emergency ratio must be between zero and one")

    random = Random(seed)
    node_ids = tuple(sorted(node.node_id for node in network.nodes))
    arrivals: list[ScheduledArrival] = []
    for index in range(count):
        origin = random.choice(node_ids)
        destination = random.choice(tuple(node for node in node_ids if node != origin))
        arrival_time = float(random.randint(0, horizon_seconds))
        emergency = random.random() < emergency_ratio
        subtype = random.choice(_EMERGENCY_SUBTYPES) if emergency else None
        arrivals.append(
            scheduled_arrival(
                network,
                vehicle_id=f"seed-{seed}-vehicle-{index + 1:03d}",
                origin=origin,
                destination=destination,
                arrival_time_seconds=arrival_time,
                emergency_subtype=subtype,
            )
        )
    return tuple(
        sorted(
            arrivals,
            key=lambda item: (item.arrival_time_seconds, item.vehicle.vehicle_id),
        )
    )
