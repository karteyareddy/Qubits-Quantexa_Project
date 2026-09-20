'use client';

import React from 'react';
import { WebSocketConnectionStatus } from '../../lib/types';
import { formatTime } from '../../lib/formatters';
import { useTheme } from '../../context/ThemeContext';

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
  const { theme, toggleTheme } = useTheme();

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
    <header className="ops-header px-6 py-4 flex flex-wrap items-center justify-between gap-4">
      {/* Brand & Mission Statement */}
      <div className="header-brand flex items-center space-x-3.5">
        <div className="header-logo-icon" style={{ padding: '2px', background: 'transparent' }}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={theme === 'light' ? '/q-trafficx-icon.png' : '/q-trafficx-icon-white.png'}
            alt="Q-TrafficX Logo"
            className="w-8 h-8 object-contain"
            style={{ width: '2rem', height: '2rem' }}
          />
        </div>
        <div>
          <h1 className="text-xl font-extrabold tracking-tight flex items-center gap-2">
            <span>Q-Traffic<span style={{ color: '#00ff9d' }}>X</span></span>
            <span className="text-slate-400 text-sm font-medium">Console</span>
          </h1>
          <p className="text-xs text-slate-400 font-medium">
            Quantum-Enhanced Adaptive Urban Traffic Optimization & Route Guidance
          </p>
        </div>
      </div>

      {/* Telemetry & Controls */}
      <div className="header-telemetry flex items-center space-x-4">
        {/* Simulation Time Clock Display */}
        <div className="header-clock px-4 py-2 rounded-xl flex flex-col items-center justify-center min-w-[140px] shadow-sm">
          <span className="text-[10px] text-slate-400 block font-mono uppercase tracking-widest leading-none mb-1">
            SIMULATION CLOCK
          </span>
          <span className="text-base font-bold font-mono text-cyan-400 block leading-tight text-center">
            T = {formatTime(simulationTime)}
          </span>
        </div>

        {/* Engine Status & Session */}
        <div className="flex flex-col items-end">
          <span
            className="text-xs font-bold uppercase tracking-wider text-slate-200"
            title={`Session: ${activeSimId || 'None'}`}
          >
            {simulationStatus}
          </span>
          {scenarioName && (
            <span className="text-xs text-slate-400 truncate max-w-[130px]">
              {scenarioName}
            </span>
          )}
        </div>

        {/* Live Network Pill */}
        <div
          className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-full text-xs font-bold text-white shadow-sm ${badge.color}`}
          title={`WebSocket Status: ${wsStatus}`}
        >
          <span>{badge.label}</span>
        </div>

        {/* Theme Toggle Borderless Pill */}
        <button
          onClick={toggleTheme}
          className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-full bg-slate-800 text-xs font-bold text-slate-100 transition-all duration-200 shadow-sm hover:scale-105 active:scale-95 cursor-pointer ml-1"
          title={`Switch to ${theme === 'light' ? 'Dark' : 'Light'} Theme`}
          aria-label="Toggle light or dark theme"
        >
          <span>{theme === 'light' ? '🌙 Dark' : '☀️ Light'}</span>
        </button>
      </div>
    </header>
  );
};
