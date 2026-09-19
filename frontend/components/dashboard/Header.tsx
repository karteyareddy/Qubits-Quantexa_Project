'use client';

import React from 'react';
import { WebSocketConnectionStatus } from '../../lib/types';
import { formatTime } from '../../lib/formatters';

interface HeaderProps {
  simulationTime: number;
  simulationStatus: string;
  wsStatus: WebSocketConnectionStatus;
  scenarioName?: string;
  activeSimId?: string | null;
}

export const Header: React.FC<HeaderProps> = ({
  simulationTime,
  simulationStatus,
  wsStatus,
  scenarioName,
  activeSimId,
}) => {
  const getWsBadge = () => {
    switch (wsStatus) {
      case 'LIVE':
        return { color: 'bg-emerald-500', label: '● LIVE' };
      case 'CONNECTING':
        return { color: 'bg-amber-500', label: '◐ CONNECTING' };
      case 'PAUSED':
        return { color: 'bg-blue-500', label: '⏸ PAUSED' };
      case 'ERROR':
        return { color: 'bg-rose-500', label: '✕ ERROR' };
      default:
        return { color: 'bg-slate-500', label: '○ DISCONNECTED' };
    }
  };

  const badge = getWsBadge();

  return (
    <header className="bg-slate-900 border-b border-slate-800 text-slate-100 px-6 py-4 flex flex-wrap items-center justify-between gap-4 shadow-lg">
      <div className="flex items-center space-x-4">
        <div className="bg-gradient-to-tr from-cyan-600 to-indigo-600 p-2.5 rounded-xl shadow-md">
          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 10V3L4 14h7v7l9-11h-7z"
            />
          </svg>
        </div>
        <div>
          <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-cyan-400 via-sky-200 to-indigo-300 bg-clip-text text-transparent">
            Quantum Traffic Control Center
          </h1>
          <p className="text-xs text-slate-400 font-medium">
            Hybrid QAOA Signal Optimization Engine & Dynamic Corridor System
          </p>
        </div>
      </div>

      <div className="flex items-center space-x-6">
        {/* Technical Quantum Status */}
        <div className="hidden lg:flex items-center space-x-2 bg-slate-950/80 px-3 py-1.5 rounded-lg border border-slate-800 text-xs">
          <span className="text-cyan-400 font-semibold">Qiskit Aer</span>
          <span className="text-slate-500">|</span>
          <span className="text-slate-300">QAOA p=1</span>
        </div>

        {/* Simulation Time Display */}
        <div className="bg-slate-950 px-4 py-1.5 rounded-lg border border-cyan-900/40 text-center">
          <span className="text-xs text-slate-400 block font-mono">SIMULATION TIME</span>
          <span className="text-lg font-bold font-mono text-cyan-300">
            T = {formatTime(simulationTime)}
          </span>
        </div>

        {/* Status Badges */}
        <div className="flex items-center space-x-3">
          <div className="flex flex-col items-end">
            <span
              className="text-xs font-semibold uppercase tracking-wider text-slate-300"
              title={`Session ID: ${activeSimId || 'None'}`}
            >
              {simulationStatus}
            </span>
            {scenarioName && (
              <span className="text-xs text-slate-400 truncate max-w-[120px]">
                {scenarioName}
              </span>
            )}
          </div>

          <div
            className={`flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold text-white shadow-sm ${badge.color}`}
            title={`WebSocket: ${wsStatus}`}
          >
            <span>{badge.label}</span>
          </div>
        </div>
      </div>
    </header>
  );
};
