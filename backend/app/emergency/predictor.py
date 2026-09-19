"""ETA prediction and green-window calculation for emergency corridors."""

from app.domain.network import Network
from app.domain.signal import SignalPhase
from app.domain.vehicle import Vehicle
from app.emergency.models import CorridorIntersectionReservation, EmergencyCorridorConfig
from app.signals.models import ApproachAxis
from app.signals.phases import approaches_for_network


class EmergencyETAPredictor:
    """Predicts arrival time and constructs green windows for emergency routes."""

    @staticmethod
    def map_incoming_edge_to_phase(
        network: Network,
        intersection_id: str,
        incoming_edge_id: str,
    ) -> SignalPhase:
        """Map incoming edge to corresponding green signal phase (NS_GREEN or EW_GREEN)."""
        approaches = approaches_for_network(network).get(intersection_id, ())
        for app in approaches:
            if app.incoming_edge_id == incoming_edge_id:
                if app.axis == ApproachAxis.EAST_WEST:
                    return SignalPhase.EW_GREEN
                return SignalPhase.NS_GREEN

        # Fallback default for unmapped approaches
        return SignalPhase.NS_GREEN

    @classmethod
    def predict_corridor_reservations(
        cls,
        vehicle: Vehicle,
        network: Network,
        sequence: list[tuple[str, str, str]],
        current_time: float,
        config: EmergencyCorridorConfig,
    ) -> list[CorridorIntersectionReservation]:
        """Calculate deterministic ETAs and green windows for each intersection in sequence."""
        if not sequence:
            return []

        edge_map = {e.edge_id: e for e in network.edges}
        route_edges = vehicle.route.edge_ids if vehicle.route else ()

        # Calculate time offset to reach each edge in route
        cumulative_time = current_time
        reservations: list[CorridorIntersectionReservation] = []

        # Track vehicle position on current edge if active
        current_edge_id = vehicle.current_edge_id

        passed_vehicle_location = current_edge_id is None

        for intersection_id, incoming_edge_id, outgoing_edge_id in sequence:
            # Traversal from current location to incoming_edge_id target (intersection_id)
            if incoming_edge_id in edge_map:
                edge = edge_map[incoming_edge_id]

                # Estimate travel time for this edge
                speed_mps = (edge.free_flow_speed_kph * 1000.0) / 3600.0
                remaining_length = edge.length_m

                if incoming_edge_id == current_edge_id:
                    remaining_length = edge.length_m * max(0.0, 1.0 - vehicle.position_on_edge)
                    passed_vehicle_location = True

                edge_travel_time = remaining_length / speed_mps if speed_mps > 0 else 5.0
                # Apply legacy congestion scaling factor
                edge_travel_time *= (1.0 + edge.congestion / 20.0)

                if not passed_vehicle_location and current_edge_id in route_edges:
                    # Vehicle hasn't reached incoming edge yet; add intervening edge travel times
                    try:
                        curr_idx = route_edges.index(current_edge_id)
                        inc_idx = route_edges.index(incoming_edge_id)
                        intervening_time = 0.0
                        for idx in range(curr_idx, inc_idx):
                            e = edge_map.get(route_edges[idx])
                            if e:
                                s_mps = (e.free_flow_speed_kph * 1000.0) / 3600.0
                                rem_len = e.length_m * (1.0 - vehicle.position_on_edge if idx == curr_idx else 1.0)
                                intervening_time += (rem_len / s_mps if s_mps > 0 else 5.0) * (1.0 + e.congestion / 20.0)
                        cumulative_time += intervening_time
                        passed_vehicle_location = True
                    except ValueError:
                        cumulative_time += edge_travel_time
                else:
                    cumulative_time += edge_travel_time

            arrival_time = cumulative_time

            # Compute green window bounds
            window_start = max(current_time, arrival_time - config.arrival_buffer_seconds)
            window_end = arrival_time + config.clearance_buffer_seconds

            required_phase = cls.map_incoming_edge_to_phase(network, intersection_id, incoming_edge_id)

            reservations.append(
                CorridorIntersectionReservation(
                    intersection_id=intersection_id,
                    arrival_time_seconds=arrival_time,
                    green_window_start=window_start,
                    green_window_end=window_end,
                    required_phase=required_phase,
                    incoming_edge_id=incoming_edge_id,
                    outgoing_edge_id=outgoing_edge_id,
                )
            )

        return reservations
