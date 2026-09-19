'use client';

import { useCallback, useEffect, useState } from 'react';
import { api } from '../lib/api';
import {
  EmergencyCorridorResponse,
  EventInjectPayload,
  EventRecordResponse,
  NetworkSchema,
  OptimizationResponse,
  ScenarioMetadataSchema,
  SimulationMetricsResponse,
  SimulationStateSnapshot,
  WebSocketConnectionStatus,
  WebSocketMessage,
} from '../lib/types';
import { useSimulationSocket } from './useSimulationSocket';

export interface MetricHistoryPoint {
  timestamp: number;
  waitingTime: number;
  throughput: number;
  queueLength: number;
}

export function useDashboard() {
  const [network, setNetwork] = useState<NetworkSchema | null>(null);
  const [scenarios, setScenarios] = useState<ScenarioMetadataSchema[]>([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState<string>('low-traffic');

  const [activeSimulationId, setActiveSimulationId] = useState<string | null>(null);
  const [simulationStatus, setSimulationStatus] = useState<string>('IDLE');
  const [simulationTime, setSimulationTime] = useState<number>(0.0);

  const [stateSnapshot, setStateSnapshot] = useState<SimulationStateSnapshot | null>(null);
  const [metrics, setMetrics] = useState<SimulationMetricsResponse | null>(null);
  const [metricHistory, setMetricHistory] = useState<MetricHistoryPoint[]>([]);

  const [latestOptimization, setLatestOptimization] = useState<OptimizationResponse | null>(null);
  const [events, setEvents] = useState<EventRecordResponse[]>([]);
  const [emergencyCorridors, setEmergencyCorridors] = useState<EmergencyCorridorResponse[]>([]);

  const [selectedIntersectionId, setSelectedIntersectionId] = useState<string | null>(null);
  const [isOptimizing, setIsOptimizing] = useState<boolean>(false);
  const [isInjectingEvent, setIsInjectingEvent] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Load static network topology & available scenarios on mount
  useEffect(() => {
    let isMounted = true;
    api
      .getNetwork()
      .then((net) => {
        if (isMounted) setNetwork(net);
      })
      .catch((err) => {
        if (isMounted) setErrorMessage(`Failed to load network: ${err.message}`);
      });

    api
      .getScenarios()
      .then((scList) => {
        if (isMounted) {
          setScenarios(scList);
          if (scList.length > 0) setSelectedScenarioId(scList[0].scenario_id);
        }
      })
      .catch((err) => {
        if (isMounted) setErrorMessage(`Failed to load scenarios: ${err.message}`);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  // Auto-create default simulation session on mount once scenarios are loaded
  useEffect(() => {
    if (scenarios.length > 0 && !activeSimulationId) {
      api
        .createSimulation({
          scenario_id: selectedScenarioId,
          duration_seconds: 120,
          control_interval_seconds: 5,
          adaptive_enabled: true,
          events_enabled: true,
          emergency_corridor_enabled: true,
        })
        .then(async (session) => {
          setActiveSimulationId(session.simulation_id);
          setSimulationStatus(session.status);
          setSimulationTime(session.simulation_time_seconds);

          const snap = await api.getSimulation(session.simulation_id);
          setStateSnapshot(snap);
        })
        .catch(() => {
          // Ignore auto-create errors if user manually triggers creation later
        });
    }
  }, [scenarios, selectedScenarioId, activeSimulationId]);

  // WebSocket message handler
  const handleWSMessage = useCallback((msg: WebSocketMessage) => {
    if (msg.type === 'state') {
      const snap = msg.data as unknown as SimulationStateSnapshot;
      setStateSnapshot(snap);
      setSimulationTime(snap.simulation_time_seconds || 0.0);
      setSimulationStatus(snap.status || 'running');

      // Update metrics if contained in snapshot
      if (snap.metrics) {
        const m = snap.metrics as unknown as SimulationMetricsResponse;
        setMetrics(m);

        setMetricHistory((prev) => {
          const point: MetricHistoryPoint = {
            timestamp: snap.simulation_time_seconds || 0,
            waitingTime: m.average_waiting_time_seconds || 0,
            throughput: m.throughput_vph || 0,
            queueLength: snap.edges ? snap.edges.reduce((acc, e) => acc + e.vehicle_count, 0) : 0,
          };
          const next = [...prev, point];
          return next.slice(-60); // Keep last 60 points
        });
      }
    } else if (msg.type === 'metrics') {
      const m = msg.data as unknown as SimulationMetricsResponse;
      setMetrics(m);
    } else if (msg.type === 'optimization') {
      const opt = msg.data as unknown as OptimizationResponse;
      setLatestOptimization(opt);
    } else if (msg.type === 'completed') {
      setSimulationStatus('completed');
    }
  }, []);

  const { status: wsStatus } = useSimulationSocket(activeSimulationId, handleWSMessage);

  // Poll metrics, events, and emergency corridors periodically while running
  useEffect(() => {
    if (!activeSimulationId) return;

    const interval = setInterval(() => {
      api
        .getEvents(activeSimulationId)
        .then(setEvents)
        .catch(() => {});
      api
        .getEmergencyCorridors(activeSimulationId)
        .then(setEmergencyCorridors)
        .catch(() => {});
      api
        .getMetrics(activeSimulationId)
        .then((m) => {
          setMetrics(m);
        })
        .catch(() => {});
    }, 2000);

    return () => clearInterval(interval);
  }, [activeSimulationId]);

  // Actions
  const createSimulation = async () => {
    setErrorMessage(null);
    try {
      const session = await api.createSimulation({
        scenario_id: selectedScenarioId,
        duration_seconds: 120,
        control_interval_seconds: 5,
        adaptive_enabled: true,
        events_enabled: true,
        emergency_corridor_enabled: true,
      });
      setActiveSimulationId(session.simulation_id);
      setSimulationStatus(session.status);
      setSimulationTime(session.simulation_time_seconds);
      setMetricHistory([]);
      setLatestOptimization(null);

      // Fetch initial state snapshot
      const snap = await api.getSimulation(session.simulation_id);
      setStateSnapshot(snap);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setErrorMessage(`Failed to create simulation: ${msg}`);
    }
  };

  const startSimulation = async () => {
    if (!activeSimulationId) return;
    setErrorMessage(null);
    try {
      const session = await api.startSimulation(activeSimulationId);
      setSimulationStatus(session.status);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setErrorMessage(`Failed to start simulation: ${msg}`);
    }
  };

  const pauseSimulation = async () => {
    if (!activeSimulationId) return;
    setErrorMessage(null);
    try {
      const session = await api.pauseSimulation(activeSimulationId);
      setSimulationStatus(session.status);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setErrorMessage(`Failed to pause simulation: ${msg}`);
    }
  };

  const stepSimulation = async (stepSeconds: number = 1.0) => {
    if (!activeSimulationId) return;
    setErrorMessage(null);
    try {
      const snap = await api.stepSimulation(activeSimulationId, stepSeconds);
      setStateSnapshot(snap);
      setSimulationTime(snap.simulation_time_seconds);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setErrorMessage(`Failed to step simulation: ${msg}`);
    }
  };

  const stopSimulation = async () => {
    if (!activeSimulationId) return;
    setErrorMessage(null);
    try {
      const session = await api.stopSimulation(activeSimulationId);
      setSimulationStatus(session.status);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setErrorMessage(`Failed to stop simulation: ${msg}`);
    }
  };

  const triggerOptimization = async () => {
    if (!activeSimulationId) return;
    setIsOptimizing(true);
    setErrorMessage(null);
    try {
      const optRes = await api.optimizeSimulation(activeSimulationId, {
        solver: 'hybrid',
        apply_immediately: true,
      });
      setLatestOptimization(optRes);

      // Refresh snapshot
      const snap = await api.getSimulation(activeSimulationId);
      setStateSnapshot(snap);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setErrorMessage(`Optimization failed: ${msg}`);
    } finally {
      setIsOptimizing(false);
    }
  };

  const injectEvent = async (payload: EventInjectPayload) => {
    if (!activeSimulationId) return;
    setIsInjectingEvent(true);
    setErrorMessage(null);
    try {
      await api.injectEvent(activeSimulationId, payload);
      const evList = await api.getEvents(activeSimulationId);
      setEvents(evList);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setErrorMessage(`Event injection failed: ${msg}`);
    } finally {
      setIsInjectingEvent(false);
    }
  };

  const activateEmergencyCorridor = async (vehicleId: string) => {
    if (!activeSimulationId) return;
    setErrorMessage(null);
    try {
      await api.activateEmergencyCorridor(activeSimulationId, vehicleId);
      const cList = await api.getEmergencyCorridors(activeSimulationId);
      setEmergencyCorridors(cList);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setErrorMessage(`Emergency corridor activation failed: ${msg}`);
    }
  };

  return {
    network,
    scenarios,
    selectedScenarioId,
    setSelectedScenarioId,
    activeSimulationId,
    simulationStatus,
    simulationTime,
    wsStatus: wsStatus as WebSocketConnectionStatus,
    stateSnapshot,
    metrics,
    metricHistory,
    latestOptimization,
    events,
    emergencyCorridors,
    selectedIntersectionId,
    setSelectedIntersectionId,
    isOptimizing,
    isInjectingEvent,
    errorMessage,
    setErrorMessage,
    createSimulation,
    startSimulation,
    pauseSimulation,
    stepSimulation,
    stopSimulation,
    triggerOptimization,
    injectEvent,
    activateEmergencyCorridor,
  };
}
