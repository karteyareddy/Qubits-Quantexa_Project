'use client';

import React from 'react';
import { SimulationStateSnapshot } from '../../lib/types';
import { formatPhaseName, formatTime } from '../../lib/formatters';

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

  const signalState = stateSnapshot?.signals?.find((s) => s.intersection_id === intersectionId);

  // Compute queued vehicles on incoming approaches to this intersection
  const incomingEdges = stateSnapshot?.edges?.filter((e) => {
    // Edge ends at this intersection (e.g. source->target where target is intersectionId)
    const parts = e.edge_id.split('-');
    return parts[1] === intersectionId;
  }) || [];

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 text-slate-100 rounded-xl shadow-2xl max-w-md w-full p-6 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-slate-200 text-lg font-bold"
        >
          ✕
        </button>

        <div className="flex items-center space-x-3 mb-4">
          <div className="bg-cyan-600/20 border border-cyan-500/40 p-2.5 rounded-lg text-cyan-400 font-bold text-lg">
            {intersectionId}
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-100">Intersection Details</h3>
            <p className="text-xs text-slate-400">Signalized Grid Node</p>
          </div>
        </div>

        {signalState ? (
          <div className="space-y-4 text-sm">
            {/* Phase Info */}
            <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
              <span className="text-xs text-slate-400 block mb-1">Active Signal Phase</span>
              <div className="flex items-center justify-between">
                <span className="font-semibold text-cyan-300">
                  {formatPhaseName(signalState.current_phase)}
                </span>
                <span className="text-xs bg-emerald-950 text-emerald-400 border border-emerald-800 px-2 py-0.5 rounded font-mono">
                  {formatTime(signalState.time_in_phase_seconds)} elapsed
                </span>
              </div>
            </div>

            {/* Active Green Approaches */}
            <div>
              <span className="text-xs font-semibold text-slate-400 block mb-2">
                Active Green Approaches
              </span>
              <div className="flex flex-wrap gap-2">
                {signalState.active_green_approaches.length > 0 ? (
                  signalState.active_green_approaches.map((app) => (
                    <span
                      key={app}
                      className="bg-emerald-950/60 border border-emerald-800/80 text-emerald-300 text-xs px-2.5 py-1 rounded font-mono"
                    >
                      ✓ {app}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-slate-500 italic">None</span>
                )}
              </div>
            </div>

            {/* Approach Queues */}
            <div>
              <span className="text-xs font-semibold text-slate-400 block mb-2">
                Incoming Approach Occupancy
              </span>
              <div className="space-y-2">
                {incomingEdges.length > 0 ? (
                  incomingEdges.map((edge) => (
                    <div
                      key={edge.edge_id}
                      className="bg-slate-950 p-2.5 rounded border border-slate-800/80 flex items-center justify-between text-xs"
                    >
                      <span className="font-mono text-slate-300">{edge.edge_id}</span>
                      <span className="font-semibold text-amber-400">
                        {edge.vehicle_count} vehicles ({edge.is_closed ? 'CLOSED' : 'OPEN'})
                      </span>
                    </div>
                  ))
                ) : (
                  <span className="text-xs text-slate-500 italic">No incoming approaches found</span>
                )}
              </div>
            </div>
          </div>
        ) : (
          <p className="text-xs text-slate-400 italic">No active signal state available for this node.</p>
        )}

        <div className="mt-6 flex justify-end">
          <button
            onClick={onClose}
            className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold px-4 py-2 rounded-lg transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
