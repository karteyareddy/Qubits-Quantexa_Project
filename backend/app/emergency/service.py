"""Service orchestrating Emergency Green Corridor lifecycles, signal preemption, and rerouting."""

from app.adaptive.controller import AdaptiveSignalPolicy
from app.domain.vehicle import VehicleState
from app.emergency.controller import EmergencyCorridorController
from app.emergency.corridor import EmergencyCorridorPlanner
from app.emergency.models import (
    CorridorStatus,
    EmergencyCorridor,
    EmergencyCorridorConfig,
    EmergencyCorridorMetrics,
)
from app.signals.policy import SignalSystem
from app.simulation.engine import TrafficSimulation


class EmergencyCorridorService:
    """Orchestrates Emergency Green Corridor lifecycles and signal priority preemption."""

    def __init__(self, config: EmergencyCorridorConfig | None = None) -> None:
        self.config = config or EmergencyCorridorConfig()
        self._corridors: dict[str, EmergencyCorridor] = {}
        self._history: list[EmergencyCorridor] = []

    @property
    def active_corridors(self) -> tuple[EmergencyCorridor, ...]:
        return tuple(c for c in self._corridors.values() if c.status == CorridorStatus.ACTIVE)

    @property
    def corridor_history(self) -> tuple[EmergencyCorridor, ...]:
        return tuple(self._history)

    def update(
        self,
        simulation: TrafficSimulation,
        signal_system: SignalSystem | None = None,
        adaptive_policy: AdaptiveSignalPolicy | None = None,
    ) -> tuple[EmergencyCorridor, ...]:
        """Update corridor lifecycles, route validation, signal preemption, and release completed corridors."""
        if not self.config.enabled:
            return ()

        current_time = simulation.state.simulation_time_seconds
        network = simulation.scenario.network

        # 1. Discover active emergency vehicles in simulation needing corridors
        all_vehicles = list(simulation.state.active_vehicles) + list(simulation.state.pending_vehicles)
        emergency_vehicles = [v for v in all_vehicles if v.is_emergency]

        for veh in emergency_vehicles:
            # Check if corridor already exists for this vehicle
            existing = [c for c in self._corridors.values() if c.vehicle_id == veh.vehicle_id]
            if not existing:
                corridor = EmergencyCorridorPlanner.plan_corridor(
                    vehicle=veh,
                    network=network,
                    current_time=current_time,
                    config=self.config,
                )
                if corridor.status == CorridorStatus.PLANNED:
                    active_corridor = corridor.model_copy(
                        update={
                            "status": CorridorStatus.ACTIVE,
                            "activated_at_seconds": current_time,
                        }
                    )
                    self._corridors[active_corridor.corridor_id] = active_corridor
                    self._history.append(active_corridor)
                else:
                    self._corridors[corridor.corridor_id] = corridor
                    self._history.append(corridor)

        # 2. Check active corridor completions and route invalidations
        for cid, corridor in list(self._corridors.items()):
            if corridor.status != CorridorStatus.ACTIVE:
                continue

            # Find matching vehicle in simulation state
            veh_match = next((v for v in all_vehicles if v.vehicle_id == corridor.vehicle_id), None)
            completed_match = next(
                (v for v in simulation.state.completed_vehicles if v.vehicle_id == corridor.vehicle_id),
                None,
            )

            if completed_match or (veh_match and veh_match.state == VehicleState.ARRIVED):
                # Emergency vehicle reached destination -> Release corridor
                released = corridor.model_copy(
                    update={
                        "status": CorridorStatus.COMPLETED,
                        "released_at_seconds": current_time,
                    }
                )
                self._corridors[cid] = released
                self._update_history(released)
                continue

            if veh_match:
                # Check if route edges are still valid / open
                edge_map = {e.edge_id: e for e in network.edges}
                has_closed_edge = any(
                    edge_id in edge_map and edge_map[edge_id].closed for edge_id in corridor.route.edge_ids
                )
                if has_closed_edge:
                    # Attempt dynamic reroute
                    replanned = EmergencyCorridorPlanner.plan_corridor(
                        vehicle=veh_match,
                        network=network,
                        current_time=current_time,
                        config=self.config,
                        corridor_id=cid,
                    )
                    if replanned.status == CorridorStatus.PLANNED:
                        updated_corridor = replanned.model_copy(
                            update={
                                "status": CorridorStatus.ACTIVE,
                                "activated_at_seconds": corridor.activated_at_seconds,
                            }
                        )
                        self._corridors[cid] = updated_corridor
                        self._update_history(updated_corridor)
                    else:
                        cancelled = corridor.model_copy(
                            update={
                                "status": CorridorStatus.CANCELLED,
                                "released_at_seconds": current_time,
                                "failure_reason": "Route blocked by closure and rerouting failed",
                            }
                        )
                        self._corridors[cid] = cancelled
                        self._update_history(cancelled)

        # 3. Apply active signal preemption overrides
        active_list = [c for c in self._corridors.values() if c.status == CorridorStatus.ACTIVE]
        if signal_system is not None:
            EmergencyCorridorController.apply_corridor_overrides(
                active_corridors=active_list,
                signal_system=signal_system,
                adaptive_policy=adaptive_policy,
                simulation_time=current_time,
            )

        return tuple(active_list)

    def _update_history(self, updated: EmergencyCorridor) -> None:
        for idx, item in enumerate(self._history):
            if item.corridor_id == updated.corridor_id:
                self._history[idx] = updated
                return
        self._history.append(updated)

    def get_metrics(self) -> tuple[EmergencyCorridorMetrics, ...]:
        """Aggregate corridor performance metrics."""
        results: list[EmergencyCorridorMetrics] = []
        for c in self._history:
            if c.status not in (CorridorStatus.ACTIVE, CorridorStatus.COMPLETED):
                continue
            act_time = c.activated_at_seconds or c.created_at_seconds
            rel_time = c.released_at_seconds
            duration = (rel_time - act_time) if rel_time is not None else 0.0

            results.append(
                EmergencyCorridorMetrics(
                    corridor_id=c.corridor_id,
                    vehicle_id=c.vehicle_id,
                    activated_at_seconds=act_time,
                    completed_at_seconds=rel_time,
                    duration_seconds=max(0.0, duration),
                    intersections_prioritized=len(c.intersections),
                )
            )
        return tuple(results)
