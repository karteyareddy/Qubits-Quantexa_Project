"""Emergency vehicle route extraction, validation, and intersection sequence identification."""

from itertools import pairwise

from app.domain.network import Network
from app.domain.route import Route
from app.domain.vehicle import Vehicle
from app.routing.routes import generate_candidate_routes


class EmergencyRouteError(Exception):
    """Raised when an emergency vehicle route is invalid or unreachable."""


class EmergencyRouteExtractor:
    """Extracts, validates, and sequences emergency routes over signalized intersections."""

    @staticmethod
    def extract_and_validate_route(
        vehicle: Vehicle,
        network: Network,
    ) -> Route:
        """Extract active route for emergency vehicle, rerouting dynamically if closed edges exist."""
        if not vehicle.is_emergency:
            raise EmergencyRouteError(f"Vehicle '{vehicle.vehicle_id}' is not an emergency vehicle.")

        route = vehicle.route
        if route is None or not route.edge_ids:
            # Generate primary candidate route
            try:
                routes = generate_candidate_routes(network, vehicle.origin, vehicle.destination)
                route = routes[0]
            except Exception as exc:
                raise EmergencyRouteError(
                    f"No valid route available from '{vehicle.origin}' to '{vehicle.destination}' for vehicle '{vehicle.vehicle_id}'."
                ) from exc

        # Check if any edge in route is closed or missing
        edge_map = {e.edge_id: e for e in network.edges}
        has_blocked_edge = False
        for edge_id in route.edge_ids:
            if edge_id not in edge_map or edge_map[edge_id].closed:
                has_blocked_edge = True
                break

        if has_blocked_edge:
            # Attempt dynamic rerouting from vehicle's current node/position to destination
            start_node = vehicle.current_node_id or vehicle.origin
            try:
                candidate_routes = generate_candidate_routes(network, start_node, vehicle.destination)
                route = candidate_routes[0]
            except Exception as exc:
                raise EmergencyRouteError(
                    f"Route for emergency vehicle '{vehicle.vehicle_id}' is blocked by road closure and rerouting failed."
                ) from exc

        return route

    @staticmethod
    def extract_intersection_sequence(
        network: Network,
        route: Route,
    ) -> list[tuple[str, str, str]]:
        """Identify ordered signalized intersections traversed by route with incoming/outgoing edges.

        Returns list of (intersection_id, incoming_edge_id, outgoing_edge_id).
        """
        edge_map = {e.edge_id: e for e in network.edges}
        intersection_ids = {n.node_id for n in network.nodes if n.is_intersection}

        if len(route.edge_ids) < 1:
            return []

        # Single edge traversal: check if target node is an intersection
        sequence: list[tuple[str, str, str]] = []

        if len(route.edge_ids) == 1:
            edge = edge_map[route.edge_ids[0]]
            if edge.target in intersection_ids:
                sequence.append((edge.target, edge.edge_id, edge.edge_id))
            return sequence

        for edge_in_id, edge_out_id in pairwise(route.edge_ids):
            edge_in = edge_map[edge_in_id]
            edge_out = edge_map[edge_out_id]
            intersection_id = edge_in.target

            if intersection_id in intersection_ids and edge_out.source == intersection_id:
                sequence.append((intersection_id, edge_in_id, edge_out_id))

        return sequence
