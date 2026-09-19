'use client';

import React from 'react';
import { MetricHistoryPoint } from '../../hooks/useDashboard';

interface MetricTrendsProps {
  history: MetricHistoryPoint[];
}

export const MetricTrends: React.FC<MetricTrendsProps> = ({ history }) => {
  if (history.length < 2) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-center text-xs text-slate-500 italic">
        Collecting live metric trends over time...
      </div>
    );
  }

  const width = 320;
  const height = 60;

  // Generate SVG path for waiting time
  const maxWait = Math.max(1, ...history.map((h) => h.waitingTime));
  const pointsWait = history
    .map((h, i) => {
      const x = (i / (history.length - 1)) * width;
      const y = height - (h.waitingTime / maxWait) * (height - 10) - 5;
      return `${x},${y}`;
    })
    .join(' ');

  // Generate SVG path for queue length
  const maxQueue = Math.max(1, ...history.map((h) => h.queueLength));
  const pointsQueue = history
    .map((h, i) => {
      const x = (i / (history.length - 1)) * width;
      const y = height - (h.queueLength / maxQueue) * (height - 10) - 5;
      return `${x},${y}`;
    })
    .join(' ');

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-md space-y-3">
      <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
        Real-Time Metric Trends (Client History)
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Waiting Time Sparkline */}
        <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
          <div className="flex justify-between text-xs mb-1">
            <span className="text-cyan-400 font-semibold">Average Waiting Time</span>
            <span className="text-slate-400 font-mono">
              {history[history.length - 1].waitingTime.toFixed(1)}s
            </span>
          </div>
          <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`}>
            <polyline fill="none" stroke="#38bdf8" strokeWidth="2" points={pointsWait} />
          </svg>
        </div>

        {/* Queue Length Sparkline */}
        <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
          <div className="flex justify-between text-xs mb-1">
            <span className="text-indigo-400 font-semibold">Total Network Queue</span>
            <span className="text-slate-400 font-mono">
              {history[history.length - 1].queueLength} veh
            </span>
          </div>
          <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`}>
            <polyline fill="none" stroke="#818cf8" strokeWidth="2" points={pointsQueue} />
          </svg>
        </div>
      </div>
    </div>
  );
};
