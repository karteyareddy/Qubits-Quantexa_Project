'use client';

import React from 'react';
import { SimulationMetricsResponse } from '../../lib/types';
import { formatNumber, formatTime } from '../../lib/formatters';

interface MetricCardsProps {
  metrics: SimulationMetricsResponse | null;
}

export const MetricCards: React.FC<MetricCardsProps> = ({ metrics }) => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      {/* Average Waiting Time */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-3 shadow-md flex flex-col justify-between">
        <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
          Avg Waiting Time
        </span>
        <div className="mt-1">
          <span className="text-xl font-bold font-mono text-cyan-300">
            {formatTime(metrics?.average_waiting_time_seconds || 0)}
          </span>
        </div>
        <span className="text-[10px] text-slate-500 mt-1">Per vehicle delay</span>
      </div>

      {/* Throughput */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-3 shadow-md flex flex-col justify-between">
        <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
          Throughput
        </span>
        <div className="mt-1">
          <span className="text-xl font-bold font-mono text-emerald-400">
            {formatNumber(metrics?.throughput_vph || 0, 0)} <span className="text-xs">v/h</span>
          </span>
        </div>
        <span className="text-[10px] text-slate-500 mt-1">Vehicles per hour</span>
      </div>

      {/* Active Vehicles */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-3 shadow-md flex flex-col justify-between">
        <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
          Active Vehicles
        </span>
        <div className="mt-1">
          <span className="text-xl font-bold font-mono text-indigo-300">
            {metrics?.active_vehicles || 0} / {metrics?.total_vehicles || 0}
          </span>
        </div>
        <span className="text-[10px] text-slate-500 mt-1">
          {formatNumber((metrics?.completion_rate || 0) * 100, 1)}% completion
        </span>
      </div>

      {/* Fuel Consumption */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-3 shadow-md flex flex-col justify-between">
        <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
          Fuel Consumed
        </span>
        <div className="mt-1">
          <span className="text-xl font-bold font-mono text-amber-300">
            {formatNumber(metrics?.total_fuel_consumed_liters || 0, 2)} <span className="text-xs">L</span>
          </span>
        </div>
        <span className="text-[10px] text-slate-500 mt-1">Environmental metric</span>
      </div>

      {/* CO2 Emissions */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-3 shadow-md flex flex-col justify-between">
        <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
          CO₂ Emitted
        </span>
        <div className="mt-1">
          <span className="text-xl font-bold font-mono text-rose-400">
            {formatNumber(metrics?.total_co2_emitted_kg || 0, 2)} <span className="text-xs">kg</span>
          </span>
        </div>
        <span className="text-[10px] text-slate-500 mt-1">Environmental impact</span>
      </div>

      {/* Emergency Corridor Status */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-3 shadow-md flex flex-col justify-between">
        <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
          Emergency Corridor
        </span>
        <div className="mt-1">
          {metrics?.emergency_corridor_active ? (
            <span className="inline-block bg-amber-950 text-amber-300 border border-amber-800 text-xs px-2.5 py-1 rounded font-bold animate-pulse">
              ⚡ ACTIVE
            </span>
          ) : (
            <span className="inline-block bg-slate-950 text-slate-400 border border-slate-800 text-xs px-2 py-0.5 rounded font-medium">
              INACTIVE
            </span>
          )}
        </div>
        <span className="text-[10px] text-slate-500 mt-1">
          Wait: {formatTime(metrics?.emergency_waiting_time_seconds || 0)}
        </span>
      </div>
    </div>
  );
};
