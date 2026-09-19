"""Signal-Control QUBO Builder constructing Q matrix, linear terms, and offsets."""

from collections import defaultdict
from collections.abc import Sequence

import dimod

from app.domain.network import Network
from app.domain.signal import SignalPhase
from app.signals.phases import approaches_for_network
from app.signals.qubo.config import SignalQuboConfig
from app.signals.qubo.objective import compute_phase_traffic_cost
from app.signals.qubo.variables import create_signal_variables
from app.simulation.models import SimulationState


class SignalQuboBuilder:
    """Constructs solver-independent Signal Control QUBO dictionary and BQM."""

    def __init__(self, config: SignalQuboConfig | None = None) -> None:
        self.config = config or SignalQuboConfig()

    def build_qubo(
        self,
        network: Network,
        state: SimulationState,
        *,
        current_phases: dict[str, SignalPhase] | None = None,
    ) -> tuple[dict[tuple[str, str], float], float, list[str], dict[tuple[str, int, int], str]]:
        """Build Signal Control QUBO dictionary and constant offset.

        Returns:
            (Q_dict, constant_offset, variable_names, variable_map)
        """
        cfg = self.config
        current = current_phases or {}

        intersections = sorted(
            node.node_id for node in network.nodes if node.is_intersection
        )
        approaches_map = approaches_for_network(network)

        legal_phases_dict: dict[str, Sequence[SignalPhase]] = {
            i_id: (SignalPhase.EW_GREEN, SignalPhase.NS_GREEN)
            for i_id in intersections
        }

        variable_map, variable_names = create_signal_variables(
            intersections,
            legal_phases_dict,
            cfg.horizon_intervals,
        )

        edge_queues = state.edge_queues
        edge_waiting_seconds, edge_emergency_counts = _extract_edge_state(state)

        Q: defaultdict[tuple[str, str], float] = defaultdict(float)
        constant_offset = 0.0
        A = cfg.constraint_penalty

        for intersection_id in intersections:
            approaches = approaches_map.get(intersection_id, ())
            legal_phases = legal_phases_dict[intersection_id]

            for t in range(cfg.horizon_intervals):
                # 1. Exactly-one-phase constraint: A * (sum_p x_{i,p,t} - 1)^2
                constant_offset += A

                for p_idx, phase in enumerate(legal_phases):
                    var_p = variable_map[(intersection_id, p_idx, t)]
                    # Constraint linear term: -A
                    Q[(var_p, var_p)] += -A

                    # 2. Traffic surrogate cost linear term
                    traffic_cost = compute_phase_traffic_cost(
                        intersection_id,
                        phase,
                        approaches,
                        edge_queues,
                        edge_waiting_seconds,
                        edge_emergency_counts,
                        cfg,
                    )
                    Q[(var_p, var_p)] += traffic_cost

                    # 3. Initial switching penalty (t = 0 against current phase)
                    if t == 0:
                        prev_phase = current.get(
                            intersection_id, SignalPhase.NS_GREEN
                        )
                        if phase != prev_phase:
                            Q[(var_p, var_p)] += cfg.switch_weight

                # Quadratic penalty for selecting multiple phases in interval t
                n_phases = len(legal_phases)
                for p1 in range(n_phases):
                    for p2 in range(p1 + 1, n_phases):
                        v1 = variable_map[(intersection_id, p1, t)]
                        v2 = variable_map[(intersection_id, p2, t)]
                        pair = (min(v1, v2), max(v1, v2))
                        Q[pair] += 2.0 * A

                # 4. Consecutive interval switching penalty
                if t < cfg.horizon_intervals - 1:
                    for p1, phase1 in enumerate(legal_phases):
                        for p2, phase2 in enumerate(legal_phases):
                            if phase1 != phase2:
                                v_t = variable_map[(intersection_id, p1, t)]
                                v_next = variable_map[(intersection_id, p2, t + 1)]
                                pair = (min(v_t, v_next), max(v_t, v_next))
                                Q[pair] += cfg.switch_weight

        # Normalize QUBO dictionary keys so u <= v
        normalized_Q: dict[tuple[str, str], float] = {}
        for (u, v), val in Q.items():
            if val != 0.0:
                key = (min(u, v), max(u, v))
                normalized_Q[key] = normalized_Q.get(key, 0.0) + val

        return normalized_Q, constant_offset, variable_names, variable_map

    def build_bqm(
        self,
        Q: dict[tuple[str, str], float],
    ) -> dimod.BinaryQuadraticModel:
        """Convert QUBO dictionary into BinaryQuadraticModel."""
        return dimod.BinaryQuadraticModel.from_qubo(Q)  # type: ignore[no-any-return]


def _extract_edge_state(
    state: SimulationState,
) -> tuple[dict[str, float], dict[str, int]]:
    """Extract aggregated waiting times and emergency counts per edge."""
    vehicle_map = {
        v.vehicle_id: v
        for v in (*state.active_vehicles, *state.completed_vehicles)
    }

    edge_waiting: defaultdict[str, float] = defaultdict(float)
    edge_emergency: defaultdict[str, int] = defaultdict(int)

    for edge_id, waiting_vids in state.edge_queues.items():
        for vid in waiting_vids:
            vehicle = vehicle_map.get(vid)
            if vehicle is not None:
                edge_waiting[edge_id] += vehicle.waiting_time_seconds
                if vehicle.is_emergency:
                    edge_emergency[edge_id] += 1

    return dict(edge_waiting), dict(edge_emergency)
