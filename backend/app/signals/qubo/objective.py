"""Traffic surrogate cost calculations for Signal-Control QUBO."""

from collections.abc import Mapping, Sequence

from app.domain.signal import SignalPhase
from app.signals.models import ApproachAxis, SignalApproach
from app.signals.phases import indication_for_phase
from app.signals.qubo.config import SignalQuboConfig


def compute_phase_traffic_cost(
    intersection_id: str,
    phase: SignalPhase,
    approaches: Sequence[SignalApproach],
    edge_queues: Mapping[str, Sequence[str]],
    edge_waiting_seconds: Mapping[str, float],
    edge_emergency_counts: Mapping[str, int],
    config: SignalQuboConfig,
) -> float:
    """Calculate the traffic surrogate cost coefficient for selecting phase at intersection.

    Unserved approaches add queue, waiting, and emergency penalties.
    Served approaches credit throughput rewards.
    """
    total_cost = 0.0

    for approach in approaches:
        if approach.intersection_id != intersection_id:
            continue

        edge_id = approach.incoming_edge_id
        q_len = len(edge_queues.get(edge_id, ()))
        w_sec = edge_waiting_seconds.get(edge_id, 0.0)
        em_count = edge_emergency_counts.get(edge_id, 0)

        # Check if phase gives GREEN indication to this approach's axis
        is_green = _is_approach_green(approach.axis, phase)

        if is_green:
            # Served approach: throughput reward
            servable = min(float(q_len), config.capacity_per_interval_veh)
            total_cost -= config.throughput_weight * servable
        else:
            # Unserved (RED) approach: queue, waiting, and emergency penalties
            q_cost = config.queue_weight * q_len
            w_cost = config.waiting_weight * w_sec
            em_cost = config.emergency_weight * em_count
            total_cost += q_cost + w_cost + em_cost

    return total_cost


def _is_approach_green(axis: ApproachAxis, phase: SignalPhase) -> bool:
    from app.domain.signal import SignalIndication

    return indication_for_phase(axis, phase) is SignalIndication.GREEN
