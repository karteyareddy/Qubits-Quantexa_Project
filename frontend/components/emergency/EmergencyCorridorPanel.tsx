'use client';

import React from 'react';
import { EmergencyCorridorResponse } from '../../lib/types';
import { formatTime } from '../../lib/formatters';

interface EmergencyCorridorPanelProps {
  corridors: EmergencyCorridorResponse[];
  onActivateCorridor?: (vehicleId: string) => void;
}

export const EmergencyCorridorPanel: React.FC<EmergencyCorridorPanelProps> = ({
  corridors,
}) => {
  const activeCorridor = corridors.find(
    (c) => c.status.toLowerCase() === 'active' || c.status.toLowerCase() === 'planned'
  );

  if (!activeCorridor) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-md text-xs">
        <div className="flex justify-between items-center mb-2">
          <h3 className="font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5">
            <span>🚑</span>
            <span>EMERGENCY GREEN CORRIDOR</span>
          </h3>
          <span className="text-[10px] bg-slate-950 text-slate-500 px-2 py-0.5 rounded">
            INACTIVE
          </span>
        </div>
        <p className="text-slate-500 italic">No active emergency vehicle green corridor.</p>
      </div>
    );
  }

  return (
    <div className="bg-slate-900 border border-amber-600/40 rounded-xl p-4 shadow-xl space-y-3">
      <div className="flex justify-between items-center">
        <h3 className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center space-x-2">
          <span>🚑</span>
          <span>EMERGENCY GREEN CORRIDOR ACTIVE</span>
        </h3>
        <span className="text-xs bg-amber-950 text-amber-300 border border-amber-800 px-2.5 py-0.5 rounded font-bold animate-pulse">
          {activeCorridor.status.toUpperCase()}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
          <span className="text-slate-400 text-[10px] block">VEHICLE ID</span>
          <span className="font-semibold text-amber-300">{activeCorridor.vehicle_id}</span>
        </div>

        <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
          <span className="text-slate-400 text-[10px] block">ROUTE INTERSECTIONS</span>
          <span className="font-mono text-slate-200">
            {activeCorridor.intersections.join(' → ')}
          </span>
        </div>
      </div>

      {/* Reserved Green Windows */}
      <div>
        <span className="text-[11px] font-semibold text-slate-400 block mb-1">
          Reserved Signal Green Windows
        </span>
        <div className="space-y-1.5">
          {activeCorridor.green_windows.map((gw) => (
            <div
              key={gw.intersection_id}
              className="bg-slate-950 p-2 rounded border border-slate-800 flex items-center justify-between text-xs font-mono"
            >
              <span className="text-slate-200 font-bold">{gw.intersection_id}</span>
              <span className="text-emerald-400">
                Window: {formatTime(gw.window_start_seconds)} - {formatTime(gw.window_end_seconds)}
              </span>
              <span className="text-slate-400 text-[10px]">
                {gw.incoming_approach} → {gw.outgoing_approach}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
