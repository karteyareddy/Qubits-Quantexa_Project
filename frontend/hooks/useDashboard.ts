'use client';

import { useCallback, useEffect, useState } from 'react';
import { api, ApiError } from '../lib/api';
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
  fuelLiters: number;
  co2Kg: number;
  completionRate: number;
}

export function useDashboard() {
  const [network, setNetwork] = useState<NetworkSchema | null>(null);
  const [scenarios, setScenarios] = useState<ScenarioMetadataSchema[]>([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState<string>('low-traffic');

  const [activeSimulationId, setActiveSimulationId] = useState<string | null>(null);
  const [simulationStatus, setSimulationStatus] = useState<string>('IDLE');
  const [simulationTime, setSimulationTime] = useState<number>(0.0);
  const [simulationSpeed, setSimulationSpeed] = useState<number>(1);

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

  const recoverMissingSimulation = useCallback((error: unknown) => {
    if (!(error instanceof ApiError) || error.status !== 404) return false;
    setActiveSimulationId(null);
    setSimulationStatus('IDLE');
    setSimulationTime(0);
    setStateSnapshot(null);
    setMetrics(null);
    setMetricHistory([]);
    setLatestOptimization(null);
    setEvents([]);
    setEmergencyCorridors([]);
    setErrorMessage(null);
    return true;
  }, []);

  const applySnapshot = useCallback((snapshot: SimulationStateSnapshot) => {
    setStateSnapshot(snapshot);
    setSimulationTime(snapshot.simulation_time_seconds);
    setSimulationStatus(snapshot.status);
    setMetrics(snapshot.metrics);
    setEmergencyCorridors(snapshot.emergency_corridors);
    setErrorMessage((current) =>
      current?.startsWith('Live simulation update failed:') ? null : current
    );
    if (snapshot.latest_optimization) {
      setLatestOptimization(snapshot.latest_optimization);
    }

    setMetricHistory((previous) => {
      const point: MetricHistoryPoint = {
        timestamp: snapshot.simulation_time_seconds,
        waitingTime: snapshot.metrics.average_waiting_time_seconds,
        throughput: snapshot.metrics.throughput_vph,
        queueLength: snapshot.edges.reduce((total, edge) => total + edge.vehicle_count, 0),
        fuelLiters: snapshot.metrics.total_fuel_consumed_liters,
        co2Kg: snapshot.metrics.total_co2_emitted_kg,
        completionRate: snapshot.metrics.completion_rate,
      };
      const lastPoint = previous.at(-1);
      if (lastPoint?.timestamp === point.timestamp) return previous;
      return [...previous, point].slice(-60);
    });
  }, []);

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

  // Auto-create default simulation session on mount once scenarios are loaded & auto-start it
  useEffect(() => {
    if (scenarios.length > 0 && !activeSimulationId) {
      api
        .createSimulation({
          scenario_id: selectedScenarioId,
          control_interval_seconds: 5,
          adaptive_enabled: true,
          events_enabled: true,
          emergency_corridor_enabled: true,
        })
        .then(async (session) => {
          setActiveSimulationId(session.simulation_id);
          setSimulationTime(session.simulation_time_seconds);

          // Auto-start simulation execution
          const started = await api.startSimulation(session.simulation_id);
          setSimulationStatus(started.status);

          const snap = await api.getSimulation(session.simulation_id);
          applySnapshot(snap);
        })
        .catch((err: unknown) => {
          const message = err instanceof Error ? err.message : String(err);
          setErrorMessage(`Failed to initialize simulation: ${message}`);
        });
    }
  }, [scenarios, selectedScenarioId, activeSimulationId, applySnapshot]);

  // Auto-tick simulation when status is 'running'
  useEffect(() => {
    if (!activeSimulationId || simulationStatus.toLowerCase() !== 'running') return;

    let isStepping = false;
    const tickInterval = setInterval(() => {
      if (isStepping) return;
      isStepping = true;
      api
        .stepSimulation(activeSimulationId, simulationSpeed)
        .then((snap) => {
          applySnapshot(snap);
        })
        .catch((err: unknown) => {
          if (recoverMissingSimulation(err)) return;
          const message = err instanceof Error ? err.message : String(err);
          setErrorMessage(`Live simulation update failed: ${message}`);
        })
        .finally(() => {
          isStepping = false;
        });
    }, 1000);

    return () => clearInterval(tickInterval);
  }, [activeSimulationId, simulationStatus, simulationSpeed, applySnapshot, recoverMissingSimulation]);

  // WebSocket message handler
  const handleWSMessage = useCallback((msg: WebSocketMessage) => {
    if (msg.type === 'state') {
      applySnapshot(msg.data as unknown as SimulationStateSnapshot);
    } else if (msg.type === 'metrics') {
      const m = msg.data as unknown as SimulationMetricsResponse;
      setMetrics(m);
    } else if (msg.type === 'optimization') {
      const opt = msg.data as unknown as OptimizationResponse;
      setLatestOptimization(opt);
    } else if (msg.type === 'completed') {
      setSimulationStatus('completed');
    }
  }, [applySnapshot]);

  const { status: wsStatus } = useSimulationSocket(activeSimulationId, handleWSMessage);

  // Poll metrics, events, and emergency corridors periodically while running
  useEffect(() => {
    if (!activeSimulationId) return;

    const refreshRuntimeData = () => {
      Promise.all([
        api.getEvents(activeSimulationId),
        api.getEmergencyCorridors(activeSimulationId),
        api.getMetrics(activeSimulationId),
      ])
        .then(([eventList, corridorList, currentMetrics]) => {
          setEvents(eventList);
          setEmergencyCorridors(corridorList);
          setMetrics(currentMetrics);
        })
        .catch(recoverMissingSimulation);
    };

    refreshRuntimeData();
    const interval = setInterval(refreshRuntimeData, 2000);

    return () => clearInterval(interval);
  }, [activeSimulationId, recoverMissingSimulation]);

  // Actions
  const createSimulation = async () => {
    setErrorMessage(null);
    try {
      const session = await api.createSimulation({
        scenario_id: selectedScenarioId,
        control_interval_seconds: 5,
        adaptive_enabled: true,
        events_enabled: true,
        emergency_corridor_enabled: true,
      });
      setActiveSimulationId(session.simulation_id);
      setSimulationTime(session.simulation_time_seconds);
      setMetricHistory([]);
      setLatestOptimization(null);

      // Auto-start simulation execution
      const started = await api.startSimulation(session.simulation_id);
      setSimulationStatus(started.status);

      // Fetch initial state snapshot
      const snap = await api.getSimulation(session.simulation_id);
      applySnapshot(snap);
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
      applySnapshot(snap);
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
      // Refresh snapshot
      const snap = await api.getSimulation(activeSimulationId);
      applySnapshot(snap);
      setLatestOptimization(optRes);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setErrorMessage(`Optimization failed: ${msg}`);
    } finally {
      setIsOptimizing(false);
    }
  };

  const injectEvent = async (payload: EventInjectPayload) => {
    if (!activeSimulationId) return false;
    setIsInjectingEvent(true);
    setErrorMessage(null);
    try {
      await api.injectEvent(activeSimulationId, payload);
      const evList = await api.getEvents(activeSimulationId);
      setEvents(evList);
      return true;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setErrorMessage(`Event injection failed: ${msg}`);
      return false;
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

  const selectScenario = async (scenarioId: string) => {
    setSelectedScenarioId(scenarioId);
    setErrorMessage(null);
    try {
      if (activeSimulationId) {
        await api.stopSimulation(activeSimulationId);
      }
      const session = await api.createSimulation({
        scenario_id: scenarioId,
        control_interval_seconds: 5,
        adaptive_enabled: true,
        events_enabled: true,
        emergency_corridor_enabled: true,
      });
      setActiveSimulationId(session.simulation_id);
      setSimulationTime(session.simulation_time_seconds);
      setMetricHistory([]);
      setLatestOptimization(null);
      setEvents([]);
      setEmergencyCorridors([]);

      // Auto-start simulation execution
      const started = await api.startSimulation(session.simulation_id);
      setSimulationStatus(started.status);

      // Fetch initial state snapshot
      const snap = await api.getSimulation(session.simulation_id);
      applySnapshot(snap);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setErrorMessage(`Failed to switch scenario: ${msg}`);
    }
  };

  return {
    network,
    scenarios,
    selectedScenarioId,
    setSelectedScenarioId: selectScenario,
    activeSimulationId,
    simulationStatus,
    simulationTime,
    simulationSpeed,
    setSimulationSpeed,
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
