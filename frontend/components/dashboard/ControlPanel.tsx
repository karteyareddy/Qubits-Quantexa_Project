'use client';

import React from 'react';
import { ScenarioMetadataSchema } from '../../lib/types';
import LatticeLoader from '../ui/LatticeLoader';

interface ControlPanelProps {
  scenarios: ScenarioMetadataSchema[];
  selectedScenarioId: string;
  onSelectScenario: (id: string) => void;
  activeSimId: string | null;
  simulationStatus: string;
  simulationSpeed: number;
  onChangeSpeed: (speed: number) => void;
  onCreateSimulation: () => void;
  onStartSimulation: () => void;
  onPauseSimulation: () => void;
  onStepSimulation: () => void;
  onSkipSimulation: () => void;
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
  simulationSpeed,
  onChangeSpeed,
  onCreateSimulation,
  onStartSimulation,
  onPauseSimulation,
  onStepSimulation,
  onSkipSimulation,
  onStopSimulation,
  onTriggerOptimization,
  onOpenInjectEvent,
  isOptimizing,
}) => {
  const isRunning = simulationStatus.toLowerCase() === 'running';
  const isPaused = simulationStatus.toLowerCase() === 'paused';
  const isCreated = simulationStatus.toLowerCase() === 'created';
  const isFinished = ['completed', 'failed'].includes(simulationStatus.toLowerCase());
  const hasActiveSession = Boolean(activeSimId);

  return (
    <div className="ops-control-bar rounded-2xl p-4 shadow-xl flex flex-wrap items-center justify-between gap-4">
      {/* Scenario Selector & Session Initialization */}
      <div className="control-scenario flex items-center space-x-3">
        <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">
          Scenario:
        </label>
        <select
          value={selectedScenarioId}
          onChange={(e) => onSelectScenario(e.target.value)}
          className="bg-slate-900/90 text-slate-100 text-xs rounded-xl px-3.5 py-2 font-semibold shadow-inner focus:outline-none focus:ring-2 focus:ring-cyan-400 cursor-pointer"
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
            className="btn-ctl btn-ctl-optimize"
          >
            <span>Initialize Session</span>
          </button>
        )}
        {hasActiveSession && isFinished && (
          <button
            onClick={onCreateSimulation}
            className="btn-ctl btn-ctl-optimize"
          >
            <span>New Session</span>
          </button>
        )}
      </div>

      {/* Simulation Transport Controls */}
      <div className="control-transport flex items-center space-x-2">
        {hasActiveSession && !isFinished && (
          <div className="speed-control" title="Simulation speed multiplier">
            <span className="speed-control__label">Speed</span>
            {[1, 2, 5].map((speed) => (
              <button
                key={speed}
                type="button"
                onClick={() => onChangeSpeed(speed)}
                className={simulationSpeed === speed ? 'speed-control__button is-active' : 'speed-control__button'}
              >
                {speed}×
              </button>
            ))}
          </div>
        )}

        {hasActiveSession && (isCreated || isPaused) && (
          <button
            onClick={onStartSimulation}
            className="btn-ctl btn-ctl-start"
          >
            <span>▶ Start</span>
          </button>
        )}

        {hasActiveSession && isRunning && (
          <button
            onClick={onPauseSimulation}
            className="btn-ctl btn-ctl-pause"
          >
            <span>⏸ Pause</span>
          </button>
        )}

        {hasActiveSession && !isFinished && (
          <button
            onClick={onStepSimulation}
            className="btn-ctl btn-ctl-step"
            title="Advance simulation by 1s"
          >
            <span>⏭ Step 1s</span>
          </button>
        )}

        {hasActiveSession && !isFinished && (
          <button
            onClick={onSkipSimulation}
            className="btn-ctl btn-ctl-skip"
            title="Advance simulation by 10 seconds"
          >
            <span>⏩ Skip +10s</span>
          </button>
        )}

        {hasActiveSession && !isFinished && (
          <button
            onClick={onStopSimulation}
            className="btn-ctl btn-ctl-stop"
          >
            <span>⏹ Stop</span>
          </button>
        )}
      </div>

      {/* Optimization & Event Action Buttons */}
      <div className="control-actions flex items-center space-x-2.5">
        <button
          onClick={onTriggerOptimization}
          disabled={!hasActiveSession || isFinished || isOptimizing}
          className="btn-ctl btn-ctl-optimize"
        >
          {isOptimizing ? (
            <LatticeLoader
              label="QAOA Solving..."
              pattern="spiral"
              grid={3}
              glow
              color="#ffffff"
              cellSize={3.5}
              gap={1.5}
              fontSize={11}
              showTimer
            />
          ) : (
            <>
              <span>⚛ Optimize Now</span>
            </>
          )}
        </button>

        <button
          onClick={onOpenInjectEvent}
          disabled={!hasActiveSession || isFinished}
          className="btn-ctl btn-ctl-event"
        >
          <span>⚡ Inject Event</span>
        </button>
      </div>
    </div>
  );
};
