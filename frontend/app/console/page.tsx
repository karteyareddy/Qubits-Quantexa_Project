'use client';

import React, { useState } from 'react';
import { useDashboard } from '../../hooks/useDashboard';
import { Header } from '../../components/dashboard/Header';
import { ControlPanel } from '../../components/dashboard/ControlPanel';
import { Sidebar } from '../../components/dashboard/Sidebar';
import { TrafficMap } from '../../components/traffic/TrafficMap';
import { IntersectionDetailModal } from '../../components/traffic/IntersectionDetailModal';
import { MetricCards } from '../../components/metrics/MetricCards';
import { MetricTrends } from '../../components/metrics/MetricTrends';
import { QuantumPanel } from '../../components/quantum/QuantumPanel';
import { ClassicalComparison } from '../../components/quantum/ClassicalComparison';
import { EmergencyCorridorPanel } from '../../components/emergency/EmergencyCorridorPanel';
import { EventTimeline } from '../../components/events/EventTimeline';
import { EventInjectionModal } from '../../components/events/EventInjectionModal';
import { WeatherControlPanel } from '../../components/weather/WeatherControlPanel';
import { TravelerAdvisoryPanel } from '../../components/routes/TravelerAdvisoryPanel';

export default function ConsolePage() {
  const {
    network,
    scenarios,
    selectedScenarioId,
    setSelectedScenarioId,
    activeSimulationId,
    simulationStatus,
    simulationTime,
    simulationSpeed,
    setSimulationSpeed,
    wsStatus,
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
  } = useDashboard();

  const [isInjectModalOpen, setIsInjectModalOpen] = useState<boolean>(false);
  const [highlightedRouteNodes, setHighlightedRouteNodes] = useState<string[] | null>(null);
  const [highlightedRouteType, setHighlightedRouteType] = useState<'direct' | 'alternative' | null>(null);

  React.useEffect(() => {
    if (typeof window !== 'undefined') {
      const nav = window.performance && window.performance.getEntriesByType && (window.performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming | undefined);
      const isNavReload = (nav && nav.type === 'reload') || (window.performance && (window.performance as any).navigation?.type === 1);
      const isStorageReload = sessionStorage.getItem('site_reloading') === '1';
      if (isNavReload || isStorageReload) {
        sessionStorage.removeItem('site_reloading');
        window.location.replace('/');
      }
    }
  }, []);

  const activeScenario = scenarios.find((s) => s.scenario_id === selectedScenarioId);

  return (
    <div className="command-shell min-h-screen bg-slate-950 text-slate-100 font-sans">
      {/* Dynamic Animated Quantum Urban Traffic Background */}
      <div className="quantum-traffic-bg" aria-hidden="true">
        <div className="ambient-glow-cyan" />
        <div className="ambient-glow-indigo" />
        <div className="ambient-traffic-grid" />
        <div className="traffic-pulse-stream" />
      </div>

      <Sidebar simulationStatus={simulationStatus} wsStatus={wsStatus} />

      <div className="command-workspace">
        <Header
          simulationTime={simulationTime}
          simulationStatus={simulationStatus}
          wsStatus={wsStatus}
          scenarioName={activeScenario?.name}
          activeSimId={activeSimulationId}
        />

        <main className="ops-main" id="overview">
          {errorMessage && (
            <div className="error-banner">
              <span className="font-semibold">⚠ {errorMessage}</span>
              <button onClick={() => setErrorMessage(null)} aria-label="Dismiss error">✕</button>
            </div>
          )}

          <ControlPanel
            scenarios={scenarios}
            selectedScenarioId={selectedScenarioId}
            onSelectScenario={setSelectedScenarioId}
            activeSimId={activeSimulationId}
            simulationStatus={simulationStatus}
            simulationSpeed={simulationSpeed}
            onChangeSpeed={setSimulationSpeed}
            onCreateSimulation={createSimulation}
            onStartSimulation={startSimulation}
            onPauseSimulation={pauseSimulation}
            onStepSimulation={() => stepSimulation(1)}
            onSkipSimulation={() => stepSimulation(10)}
            onStopSimulation={stopSimulation}
            onTriggerOptimization={triggerOptimization}
            onOpenInjectEvent={() => setIsInjectModalOpen(true)}
            isOptimizing={isOptimizing}
          />

          <MetricCards metrics={metrics} />

          <div className="mission-grid">
            <section className="mission-network" id="network">
              <TrafficMap
                network={network}
                stateSnapshot={stateSnapshot}
                emergencyCorridors={emergencyCorridors}
                selectedIntersectionId={selectedIntersectionId}
                onSelectIntersection={setSelectedIntersectionId}
                highlightedRouteNodes={highlightedRouteNodes}
                highlightedRouteType={highlightedRouteType}
              />
            </section>

            <aside className="mission-rail">
              <QuantumPanel id="quantum" latestOptimization={latestOptimization} isOptimizing={isOptimizing} />
              <EmergencyCorridorPanel id="emergency" corridors={emergencyCorridors} onActivateCorridor={activateEmergencyCorridor} />
            </aside>
          </div>

          {/* Weather Intelligence & Dynamic Traveler Advisory Section */}
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 my-4">
            <WeatherControlPanel id="weather" />
            <TravelerAdvisoryPanel
              id="advisory"
              onSelectRouteForHighlight={(nodes, type) => {
                setHighlightedRouteNodes(nodes);
                setHighlightedRouteType(type);
              }}
            />
          </div>

          <MetricTrends history={metricHistory} />

          <div className="lower-deck">
            <ClassicalComparison id="comparison" latestOptimization={latestOptimization} />
            <EventTimeline id="events" events={events} />
          </div>
        </main>
      </div>

      {/* Modals */}
      <IntersectionDetailModal
        intersectionId={selectedIntersectionId}
        stateSnapshot={stateSnapshot}
        onClose={() => setSelectedIntersectionId(null)}
      />

      {isInjectModalOpen && (
        <EventInjectionModal
          simulationTime={simulationTime}
          network={network}
          onInject={async (payload) => {
            const accepted = await injectEvent(payload);
            if (accepted) setIsInjectModalOpen(false);
          }}
          onClose={() => setIsInjectModalOpen(false)}
          isInjecting={isInjectingEvent}
        />
      )}
    </div>
  );
}
