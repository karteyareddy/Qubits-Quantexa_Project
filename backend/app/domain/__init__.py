"""Typed domain contracts for the traffic optimization backend."""

from app.domain.emergency import EmergencyMission, EmergencyMissionStatus
from app.domain.event import EventStatus, EventType, TrafficEvent
from app.domain.metrics import (
    EdgeTrafficMetrics,
    EmergencyMetrics,
    EnvironmentalMetrics,
    IntersectionApproachMetrics,
    ScenarioMetrics,
    TrafficMetrics,
    VehicleMetrics,
)
from app.domain.network import Coordinates, Network, NetworkEdge, NetworkNode
from app.domain.optimization import (
    ExecutionClass,
    FeasibilityResult,
    OptimizationPlan,
    OptimizationResult,
    OptimizationType,
    SolverMetadata,
)
from app.domain.route import Route
from app.domain.scenario import Scenario, ScenarioConfiguration
from app.domain.signal_qubo import (
    IntervalSignalDecision,
    SignalQuboResult,
    SignalSchedule,
)
from app.domain.vehicle import EmergencySubtype, Vehicle, VehicleState, VehicleType

__all__ = [
    "ApproachSignalState",
    "Coordinates",
    "EdgeTrafficMetrics",
    "EmergencyMetrics",
    "EmergencyMission",
    "EmergencyMissionStatus",
    "EmergencySubtype",
    "EnvironmentalMetrics",
    "EventStatus",
    "EventType",
    "ExecutionClass",
    "FeasibilityResult",
    "IntersectionApproachMetrics",
    "IntervalSignalDecision",
    "Network",
    "NetworkEdge",
    "NetworkNode",
    "OptimizationPlan",
    "OptimizationResult",
    "OptimizationType",
    "Route",
    "Scenario",
    "ScenarioConfiguration",
    "ScenarioMetrics",
    "SignalIndication",
    "SignalPhase",
    "SignalQuboResult",
    "SignalSchedule",
    "SignalState",
    "SolverMetadata",
    "TrafficEvent",
    "TrafficMetrics",
    "Vehicle",
    "VehicleMetrics",
    "VehicleState",
    "VehicleType",
]
