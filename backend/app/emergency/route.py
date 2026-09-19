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

        # Only inspect the route that the vehicle has not traversed yet. A vehicle
        # already occupying an edge is allowed to clear it before taking a detour.
        edge_map = {e.edge_id: e for e in network.edges}
        first_untraversed_index = (
            vehicle.current_route_index + 1 if vehicle.current_edge_id is not None else 0
        )
        remaining_edge_ids = route.edge_ids[first_untraversed_index:]
        has_blocked_edge = any(
            edge_id not in edge_map or edge_map[edge_id].closed
            for edge_id in remaining_edge_ids
        )

        if has_blocked_edge:
            # Finish the current edge, then route from its target. This preserves
            # physical continuity while avoiding every closed edge ahead.
            if vehicle.current_edge_id is not None:
                current_edge = edge_map.get(vehicle.current_edge_id)
                if current_edge is None:
                    raise EmergencyRouteError(
                        f"Current edge '{vehicle.current_edge_id}' is missing from the network."
                    )
                start_node = current_edge.target
            else:
                start_node = vehicle.current_node_id or vehicle.origin
            try:
                candidate_routes = generate_candidate_routes(network, start_node, vehicle.destination)
                detour = candidate_routes[0]
                route = EmergencyRouteExtractor._merge_active_route(vehicle, detour)
            except Exception as exc:
                raise EmergencyRouteError(
                    f"Route for emergency vehicle '{vehicle.vehicle_id}' is blocked by road closure and rerouting failed."
                ) from exc

        return route

    @staticmethod
    def _merge_active_route(vehicle: Vehicle, detour: Route) -> Route:
        """Join the already-traversed route prefix to a new remaining route."""
        current_route = vehicle.route
        if current_route is None or vehicle.current_edge_id is None:
            return detour

        prefix_edge_count = vehicle.current_route_index + 1
        prefix_edges = current_route.edge_ids[:prefix_edge_count]
        prefix_nodes = current_route.node_ids[: prefix_edge_count + 1]
        if not prefix_nodes or not detour.node_ids or prefix_nodes[-1] != detour.node_ids[0]:
            raise EmergencyRouteError("Detour does not connect to the vehicle's current edge.")

        edge_ids = prefix_edges + detour.edge_ids
        node_ids = prefix_nodes + detour.node_ids[1:]
        return Route(
            route_id=f"reroute:{vehicle.vehicle_id}:{detour.route_id}",
            node_ids=node_ids,
            edge_ids=edge_ids,
            estimated_travel_time_seconds=detour.estimated_travel_time_seconds,
            distance_m=detour.distance_m,
            cost=detour.cost,
        )

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
