'use client';

import React from 'react';
import { ScenarioMetadataSchema } from '../../lib/types';

interface ControlPanelProps {
  scenarios: ScenarioMetadataSchema[];
  selectedScenarioId: string;
  onSelectScenario: (id: string) => void;
  activeSimId: string | null;
  simulationStatus: string;
  onCreateSimulation: () => void;
  onStartSimulation: () => void;
  onPauseSimulation: () => void;
  onStepSimulation: () => void;
  onStopSimulation: () => void;
  onTriggerOptimization: () => void;
  onOpenInjectEvent: () => void;
  isOptimizing: boolean;
}

export const ControlPanel: React.FC<ControlPanelProps> = ({
  scenarios,
  selectedScenarioId,
  onSelectScenario,
  activeSimId,
  simulationStatus,
  onCreateSimulation,
  onStartSimulation,
  onPauseSimulation,
  onStepSimulation,
  onStopSimulation,
  onTriggerOptimization,
  onOpenInjectEvent,
  isOptimizing,
}) => {
  const isRunning = simulationStatus.toLowerCase() === 'running';
  const isPaused = simulationStatus.toLowerCase() === 'paused';
  const isCreated = simulationStatus.toLowerCase() === 'created';
  const hasActiveSession = Boolean(activeSimId);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-md flex flex-wrap items-center justify-between gap-4">
      {/* Scenario Selector & Session Initialization */}
      <div className="flex items-center space-x-3">
        <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Scenario:
        </label>
        <select
          value={selectedScenarioId}
          onChange={(e) => onSelectScenario(e.target.value)}
          disabled={hasActiveSession && isRunning}
          className="bg-slate-950 text-slate-100 border border-slate-700 text-xs rounded-lg px-3 py-2 font-medium focus:outline-none focus:border-cyan-500 disabled:opacity-50"
        >
          {scenarios.map((sc) => (
            <option key={sc.scenario_id} value={sc.scenario_id}>
              {sc.name} ({sc.vehicle_count} veh)
            </option>
          ))}
        </select>

        {!hasActiveSession && (
          <button
            onClick={onCreateSimulation}
            className="bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold px-4 py-2 rounded-lg transition-colors shadow-md flex items-center space-x-1.5"
          >
            <span>Initialize Session</span>
          </button>
        )}
      </div>

      {/* Simulation Controls */}
      <div className="flex items-center space-x-2">
        {hasActiveSession && (isCreated || isPaused) && (
          <button
            onClick={onStartSimulation}
            className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-3 py-2 rounded-lg transition-colors flex items-center space-x-1"
          >
            <span>▶ Start</span>
          </button>
        )}

        {hasActiveSession && isRunning && (
          <button
            onClick={onPauseSimulation}
            className="bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold px-3 py-2 rounded-lg transition-colors flex items-center space-x-1"
          >
            <span>⏸ Pause</span>
          </button>
        )}

        {hasActiveSession && (
          <button
            onClick={onStepSimulation}
            disabled={isRunning}
            className="bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold px-3 py-2 rounded-lg transition-colors disabled:opacity-40"
            title="Advance simulation by 1s"
          >
            <span>⏭ Step 1s</span>
          </button>
        )}

        {hasActiveSession && (
          <button
            onClick={onStopSimulation}
            className="bg-rose-700 hover:bg-rose-600 text-white text-xs font-semibold px-3 py-2 rounded-lg transition-colors flex items-center space-x-1"
          >
            <span>⏹ Stop</span>
          </button>
        )}
      </div>

      {/* Optimization & Event Actions */}
      <div className="flex items-center space-x-2">
        <button
          onClick={onTriggerOptimization}
          disabled={!hasActiveSession || isOptimizing}
          className="bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white text-xs font-bold px-4 py-2 rounded-lg shadow-md transition-all flex items-center space-x-2 disabled:opacity-40"
        >
          {isOptimizing ? (
            <>
              <svg className="animate-spin h-3.5 w-3.5 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              <span>Optimizing QAOA...</span>
            </>
          ) : (
            <>
              <span>⚛ Optimize Now</span>
            </>
          )}
        </button>

        <button
          onClick={onOpenInjectEvent}
          disabled={!hasActiveSession}
          className="bg-slate-800 hover:bg-slate-700 text-amber-300 border border-amber-600/40 text-xs font-semibold px-3.5 py-2 rounded-lg transition-colors disabled:opacity-40 flex items-center space-x-1.5"
        >
          <span>⚡ Inject Event</span>
        </button>
      </div>
    </div>
  );
};
