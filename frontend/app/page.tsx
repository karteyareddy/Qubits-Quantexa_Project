'use client';

import React, { useState } from 'react';
import { useDashboard } from '../hooks/useDashboard';
import { Header } from '../components/dashboard/Header';
import { ControlPanel } from '../components/dashboard/ControlPanel';
import { TrafficMap } from '../components/traffic/TrafficMap';
import { IntersectionDetailModal } from '../components/traffic/IntersectionDetailModal';
import { MetricCards } from '../components/metrics/MetricCards';
import { MetricTrends } from '../components/metrics/MetricTrends';
import { QuantumPanel } from '../components/quantum/QuantumPanel';
import { ClassicalComparison } from '../components/quantum/ClassicalComparison';
import { EmergencyCorridorPanel } from '../components/emergency/EmergencyCorridorPanel';
import { EventTimeline } from '../components/events/EventTimeline';
import { EventInjectionModal } from '../components/events/EventInjectionModal';

export default function Home() {
  const {
    network,
    scenarios,
    selectedScenarioId,
    setSelectedScenarioId,
    activeSimulationId,
    simulationStatus,
    simulationTime,
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

  const activeScenario = scenarios.find((s) => s.scenario_id === selectedScenarioId);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* 1. Header */}
      <Header
        simulationTime={simulationTime}
        simulationStatus={simulationStatus}
        wsStatus={wsStatus}
        scenarioName={activeScenario?.name}
        activeSimId={activeSimulationId}
      />

      {/* Main Dashboard Workspace */}
      <main className="flex-1 p-4 space-y-4 max-w-[1600px] w-full mx-auto">
        {/* Error Banner */}
        {errorMessage && (
          <div className="bg-rose-950/80 border border-rose-800 text-rose-200 text-xs px-4 py-3 rounded-xl flex items-center justify-between shadow-lg">
            <span className="font-semibold">⚠️ {errorMessage}</span>
            <button
              onClick={() => setErrorMessage(null)}
              className="text-rose-400 hover:text-white font-bold ml-4"
            >
              ✕
            </button>
          </div>
        )}

        {/* 2. Control Panel */}
        <ControlPanel
          scenarios={scenarios}
          selectedScenarioId={selectedScenarioId}
          onSelectScenario={setSelectedScenarioId}
          activeSimId={activeSimulationId}
          simulationStatus={simulationStatus}
          onCreateSimulation={createSimulation}
          onStartSimulation={startSimulation}
          onPauseSimulation={pauseSimulation}
          onStepSimulation={stepSimulation}
          onStopSimulation={stopSimulation}
          onTriggerOptimization={triggerOptimization}
          onOpenInjectEvent={() => setIsInjectModalOpen(true)}
          isOptimizing={isOptimizing}
        />

        {/* 3. Top Metrics Row */}
        <MetricCards metrics={metrics} />

        {/* 4. Main 2-Column Split: Quantum & Metrics Left | Map & Corridors Right */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          {/* Left Column (5 Cols): Quantum & Technical Panels */}
          <div className="lg:col-span-5 space-y-4">
            <QuantumPanel
              latestOptimization={latestOptimization}
              isOptimizing={isOptimizing}
            />

            <ClassicalComparison latestOptimization={latestOptimization} />

            <MetricTrends history={metricHistory} />

            <EventTimeline events={events} />
          </div>

          {/* Right Column (7 Cols): Live Map & Emergency Panels */}
          <div className="lg:col-span-7 space-y-4">
            <TrafficMap
              network={network}
              stateSnapshot={stateSnapshot}
              emergencyCorridors={emergencyCorridors}
              selectedIntersectionId={selectedIntersectionId}
              onSelectIntersection={setSelectedIntersectionId}
            />

            <EmergencyCorridorPanel
              corridors={emergencyCorridors}
              onActivateCorridor={activateEmergencyCorridor}
            />
          </div>
        </div>
      </main>

      {/* Modals */}
      <IntersectionDetailModal
        intersectionId={selectedIntersectionId}
        stateSnapshot={stateSnapshot}
        onClose={() => setSelectedIntersectionId(null)}
      />

      {isInjectModalOpen && (
        <EventInjectionModal
          simulationTime={simulationTime}
          onInject={(payload) => {
            injectEvent(payload);
            setIsInjectModalOpen(false);
          }}
          onClose={() => setIsInjectModalOpen(false)}
          isInjecting={isInjectingEvent}
        />
      )}
    </div>
  );
}
