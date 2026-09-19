'use client';

import React from 'react';
import { SimulationStateSnapshot } from '../../lib/types';
import { formatPhaseName, formatTime } from '../../lib/formatters';
import { CITY_INTERSECTIONS } from '../../lib/cityMapConfig';

interface IntersectionDetailModalProps {
  intersectionId: string | null;
  stateSnapshot: SimulationStateSnapshot | null;
  onClose: () => void;
}

export const IntersectionDetailModal: React.FC<IntersectionDetailModalProps> = ({
  intersectionId,
  stateSnapshot,
  onClose,
}) => {
  if (!intersectionId) return null;

  const cityInfo = CITY_INTERSECTIONS[intersectionId];
  const signalState = stateSnapshot?.signals?.find((s) => s.intersection_id === intersectionId);

  // Compute queued vehicles on incoming approaches to this intersection
  const incomingEdges =
    stateSnapshot?.edges?.filter((e) => {
      const parts = e.edge_id.split('-');
      return parts[1] === intersectionId;
    }) || [];

  const totalQueuedVehicles = incomingEdges.reduce((acc, e) => acc + e.vehicle_count, 0);

  return (
    <div className="fixed inset-0 bg-black/75 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900/95 border border-cyan-500/30 text-slate-100 rounded-2xl shadow-2xl max-w-lg w-full p-6 relative overflow-hidden backdrop-blur-xl">
        {/* Top ambient glow */}
        <div className="absolute -top-16 -left-16 w-48 h-48 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-16 -right-16 w-48 h-48 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors text-lg font-bold"
          aria-label="Close modal"
        >
          ✕
        </button>

        {/* Header with City Name & ID */}
        <div className="flex items-start space-x-3.5 mb-5 relative">
          <div className="bg-gradient-to-br from-cyan-600 to-blue-700 text-white font-black text-xl px-3.5 py-2.5 rounded-xl shadow-lg border border-cyan-400/40 flex flex-col items-center justify-center min-w-[52px]">
            <span>{intersectionId}</span>
            <span className="text-[9px] font-mono tracking-widest text-cyan-200 uppercase">NODE</span>
          </div>
          <div>
            <div className="flex items-center space-x-2 mb-0.5">
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-cyan-950/80 text-cyan-300 border border-cyan-800/60 font-mono uppercase tracking-wider">
                {cityInfo?.district || 'Urban District'}
              </span>
              <span className="text-xs text-slate-400 font-mono">
                {cityInfo?.speedLimit ? `Limit: ${cityInfo.speedLimit}` : '45 km/h'}
              </span>
            </div>
            <h3 className="text-xl font-bold text-white tracking-tight">
              {cityInfo?.name || `Intersection ${intersectionId}`}
            </h3>
            <p className="text-xs text-slate-300 flex items-center space-x-1.5 mt-0.5">
              <span>📍 {cityInfo?.crossStreet || 'Controlled Intersection'}</span>
            </p>
          </div>
        </div>

        {cityInfo?.landmark && (
          <div className="mb-4 bg-slate-950/70 border border-slate-800/90 rounded-xl px-3.5 py-2 text-xs flex items-center space-x-2 text-slate-300">
            <span className="text-amber-400 font-bold">🏛 Landmark:</span>
            <span>{cityInfo.landmark}</span>
          </div>
        )}

        {signalState ? (
          <div className="space-y-4 text-sm">
            {/* Phase & Optics Info */}
            <div className="bg-slate-950/90 p-3.5 rounded-xl border border-slate-800/80">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Active Traffic Signal Phase
                </span>
                <span className="text-xs bg-emerald-950/90 text-emerald-400 border border-emerald-800 px-2.5 py-0.5 rounded-full font-mono font-semibold flex items-center space-x-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping inline-block" />
                  <span>{formatTime(signalState.time_in_phase_seconds)} elapsed</span>
                </span>
              </div>

              <div className="flex items-center justify-between bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                <div className="flex items-center space-x-2.5">
                  <div className="flex space-x-1 bg-slate-950 p-1.5 rounded-lg border border-slate-800">
                    <span
                      className={`w-3.5 h-3.5 rounded-full ${
                        signalState.current_phase === 'EW_GREEN' ? 'bg-emerald-500 shadow-[0_0_8px_#22c55e]' : 'bg-red-950 border border-red-800'
                      }`}
                      title="EW Phase"
                    />
                    <span
                      className={`w-3.5 h-3.5 rounded-full ${
                        signalState.current_phase === 'NS_GREEN' ? 'bg-emerald-500 shadow-[0_0_8px_#22c55e]' : 'bg-red-950 border border-red-800'
                      }`}
                      title="NS Phase"
                    />
                  </div>
                  <span className="font-bold text-white text-base">
                    {formatPhaseName(signalState.current_phase)}
                  </span>
                </div>
                <span className="text-xs text-slate-400">
                  {signalState.current_phase === 'EW_GREEN' ? 'East-West Corridors Flowing' : 'North-South Corridors Flowing'}
                </span>
              </div>
            </div>

            {/* Active Green Approaches */}
            <div>
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
                Active Green Approaches (Right-of-Way)
              </span>
              <div className="flex flex-wrap gap-2">
                {signalState.active_green_approaches.length > 0 ? (
                  signalState.active_green_approaches.map((app) => (
                    <span
                      key={app}
                      className="bg-emerald-950/70 border border-emerald-700/80 text-emerald-300 text-xs px-3 py-1 rounded-lg font-mono font-bold flex items-center space-x-1"
                    >
                      <span>🟢</span>
                      <span>{app}</span>
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-slate-500 italic">None Active</span>
                )}
              </div>
            </div>

            {/* Approach Queues */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Inbound Approach Traffic & Queues
                </span>
                <span className="text-xs font-mono text-cyan-400">
                  Total in queue: {totalQueuedVehicles} veh
                </span>
              </div>
              <div className="space-y-2 max-h-40 overflow-y-auto pr-1">
                {incomingEdges.length > 0 ? (
                  incomingEdges.map((edge) => (
                    <div
                      key={edge.edge_id}
                      className="bg-slate-950/80 p-2.5 rounded-lg border border-slate-800 flex items-center justify-between text-xs"
                    >
                      <div className="flex items-center space-x-2">
                        <span className="font-mono font-bold text-slate-200">{edge.edge_id}</span>
                        {edge.is_closed && (
                          <span className="bg-rose-950 text-rose-400 border border-rose-800 text-[10px] px-1.5 py-0.2 rounded font-bold">
                            CLOSED
                          </span>
                        )}
                      </div>
                      <div className="flex items-center space-x-3">
                        <span className="text-slate-400">
                          Multiplier: <strong className="text-slate-200">{edge.travel_time_multiplier.toFixed(1)}×</strong>
                        </span>
                        <span className="font-bold text-amber-400 bg-amber-950/40 border border-amber-800/60 px-2 py-0.5 rounded font-mono">
                          {edge.vehicle_count} veh
                        </span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-xs text-slate-500 italic p-3 text-center bg-slate-950 rounded-lg">
                    No active inbound approaches detected
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-6 text-slate-500">
            No live signal data available for node {intersectionId}
          </div>
        )}

        <div className="mt-5 pt-3 border-t border-slate-800/80 flex justify-end">
          <button
            onClick={onClose}
            className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold px-4 py-2 rounded-lg transition-colors border border-slate-700"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
