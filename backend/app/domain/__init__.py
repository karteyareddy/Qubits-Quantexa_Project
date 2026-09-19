"""Typed domain contracts for the traffic optimization backend."""

from app.domain.emergency import EmergencyMission, EmergencyMissionStatus
from app.domain.event import EventStatus, EventType, TrafficEvent
from app.domain.metrics import EmergencyMetrics, EnvironmentalMetrics, TrafficMetrics
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
from app.domain.signal import ApproachSignalState, SignalIndication, SignalPhase, SignalState
from app.domain.vehicle import EmergencySubtype, Vehicle, VehicleState, VehicleType

__all__ = [
    "ApproachSignalState",
    "Coordinates",
    "EmergencyMetrics",
    "EmergencyMission",
    "EmergencyMissionStatus",
    "EmergencySubtype",
    "EnvironmentalMetrics",
    "EventStatus",
    "EventType",
    "ExecutionClass",
    "FeasibilityResult",
    "Network",
    "NetworkEdge",
    "NetworkNode",
    "OptimizationPlan",
    "OptimizationResult",
    "OptimizationType",
    "Route",
    "Scenario",
    "ScenarioConfiguration",
    "SignalIndication",
    "SignalPhase",
    "SignalState",
    "SolverMetadata",
    "TrafficEvent",
    "TrafficMetrics",
    "Vehicle",
    "VehicleState",
    "VehicleType",
]
