'use client';

import React from 'react';
import {
  EmergencyCorridorResponse,
  NetworkSchema,
  SignalStateSchema,
  SimulationStateSnapshot,
  VehicleStateSchema,
} from '../../lib/types';

interface TrafficMapProps {
  network: NetworkSchema | null;
  stateSnapshot: SimulationStateSnapshot | null;
  emergencyCorridors: EmergencyCorridorResponse[];
  selectedIntersectionId: string | null;
  onSelectIntersection: (id: string) => void;
}

// Fixed coordinates for schematic rendering of 6-intersection grid
const NODE_POSITIONS: Record<string, { x: number; y: number; label: string }> = {
  I1: { x: 120, y: 100, label: 'I1 (NW Gateway)' },
  I2: { x: 360, y: 100, label: 'I2 (North Hub)' },
  I3: { x: 600, y: 100, label: 'I3 (NE Gateway)' },
  I4: { x: 120, y: 320, label: 'I4 (SW Gateway)' },
  I5: { x: 360, y: 320, label: 'I5 (Central Hub)' },
  I6: { x: 600, y: 320, label: 'I6 (SE Gateway)' },
};

export const TrafficMap: React.FC<TrafficMapProps> = ({
  network,
  stateSnapshot,
  emergencyCorridors,
  selectedIntersectionId,
  onSelectIntersection,
}) => {
  if (!network) {
    return (
      <div className="bg-slate-950 border border-slate-800 rounded-xl p-8 text-center text-slate-400">
        Loading Network Topology...
      </div>
    );
  }

  // Map signal states by intersection_id
  const signalMap = new Map<string, SignalStateSchema>();
  stateSnapshot?.signals?.forEach((s) => signalMap.set(s.intersection_id, s));

  // Map edge occupancy and closed status from snapshot
  const edgeStateMap = new Map<string, { count: number; isClosed: boolean; capacity: number }>();
  stateSnapshot?.edges?.forEach((e) => {
    edgeStateMap.set(e.edge_id, {
      count: e.vehicle_count,
      isClosed: e.is_closed,
      capacity: e.capacity,
    });
  });

  // Extract active corridor routes
  const activeCorridor = emergencyCorridors.find(
    (c) => c.status.toLowerCase() === 'active' || c.status.toLowerCase() === 'planned'
  );

  const activeCorridorEdgeSet = new Set<string>();
  if (activeCorridor) {
    activeCorridor.route.forEach((eId) => activeCorridorEdgeSet.add(eId));
  }

  const activeCorridorNodeSet = new Set<string>(activeCorridor?.intersections || []);

  return (
    <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 shadow-xl relative overflow-hidden flex flex-col items-center">
      <div className="w-full flex justify-between items-center mb-2 px-2">
        <h2 className="text-sm font-bold text-slate-200 tracking-wider flex items-center space-x-2">
          <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse"></span>
          <span>LIVE TRAFFIC NETWORK TOPOLOGY</span>
        </h2>

        <div className="flex items-center space-x-4 text-xs">
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-1 bg-cyan-400 rounded"></span>
            <span className="text-slate-400">Normal Edge</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-1 bg-rose-500 rounded"></span>
            <span className="text-slate-400">Congested Edge</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-1 bg-amber-400 rounded shadow-[0_0_8px_rgba(251,191,36,0.8)]"></span>
            <span className="text-slate-300 font-semibold">Emergency Corridor</span>
          </div>
        </div>
      </div>

      <div className="w-full overflow-x-auto flex justify-center py-2">
        <svg width="720" height="420" className="bg-slate-950 rounded-lg select-none">
          {/* Background Grid Pattern */}
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" strokeWidth="0.5" />
            </pattern>
            <filter id="glow-emergency" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="4" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />

          {/* Render Edges */}
          {network.edges.map((edge) => {
            const srcPos = NODE_POSITIONS[edge.source_intersection];
            const tgtPos = NODE_POSITIONS[edge.target_intersection];
            if (!srcPos || !tgtPos) return null;

            const edgeInfo = edgeStateMap.get(edge.edge_id) || {
              count: 0,
              isClosed: false,
              capacity: edge.capacity,
            };
            const isCorridorEdge = activeCorridorEdgeSet.has(edge.edge_id);

            // Calculate directional offset so bidirectional edges don't overlap
            const dx = tgtPos.x - srcPos.x;
            const dy = tgtPos.y - srcPos.y;
            const len = Math.sqrt(dx * dx + dy * dy);
            const offsetX = (-dy / len) * 6;
            const offsetY = (dx / len) * 6;

            const x1 = srcPos.x + offsetX;
            const y1 = srcPos.y + offsetY;
            const x2 = tgtPos.x + offsetX;
            const y2 = tgtPos.y + offsetY;

            // Congestion color logic
            let strokeColor = '#38bdf8'; // cyan-400
            let strokeWidth = 3;

            if (edgeInfo.isClosed) {
              strokeColor = '#ef4444'; // red-500
            } else if (edgeInfo.count > 5) {
              strokeColor = '#f43f5e'; // rose-500
              strokeWidth = 4;
            } else if (edgeInfo.count > 2) {
              strokeColor = '#fbbf24'; // amber-400
              strokeWidth = 3.5;
            }

            if (isCorridorEdge) {
              strokeColor = '#fbbf24';
              strokeWidth = 6;
            }

            return (
              <g key={edge.edge_id}>
                {/* Glow underlay for corridor */}
                {isCorridorEdge && (
                  <line
                    x1={x1}
                    y1={y1}
                    x2={x2}
                    y2={y2}
                    stroke="#fbbf24"
                    strokeWidth={10}
                    strokeOpacity={0.4}
                    filter="url(#glow-emergency)"
                  />
                )}

                {/* Main Edge Line */}
                <line
                  x1={x1}
                  y1={y1}
                  x2={x2}
                  y2={y2}
                  stroke={strokeColor}
                  strokeWidth={strokeWidth}
                  strokeDasharray={edgeInfo.isClosed ? '6,4' : undefined}
                />

                {/* Edge Occupancy Label */}
                <text
                  x={(x1 + x2) / 2 + (offsetX > 0 ? 8 : -8)}
                  y={(y1 + y2) / 2 + (offsetY > 0 ? 8 : -8)}
                  fill={isCorridorEdge ? '#fbbf24' : '#94a3b8'}
                  fontSize="10"
                  fontWeight="600"
                  textAnchor="middle"
                >
                  {edgeInfo.isClosed ? 'CLOSED' : `${edgeInfo.count}v`}
                </text>
              </g>
            );
          })}

          {/* Render Vehicles */}
          {stateSnapshot?.vehicles?.map((veh: VehicleStateSchema) => {
            if (veh.has_arrived || !veh.current_edge_id) return null;

            const edge = network.edges.find((e) => e.edge_id === veh.current_edge_id);
            if (!edge) return null;

            const srcPos = NODE_POSITIONS[edge.source_intersection];
            const tgtPos = NODE_POSITIONS[edge.target_intersection];
            if (!srcPos || !tgtPos) return null;

            // Interpolate position along edge
            const ratio = Math.min(1.0, Math.max(0.0, veh.distance_on_current_edge_meters / edge.length_meters));
            const vx = srcPos.x + (tgtPos.x - srcPos.x) * ratio;
            const vy = srcPos.y + (tgtPos.y - srcPos.y) * ratio;

            if (veh.is_emergency) {
              return (
                <g key={veh.vehicle_id}>
                  <circle cx={vx} cy={vy} r="10" fill="#f59e0b" fillOpacity="0.4" className="animate-ping" />
                  <circle cx={vx} cy={vy} r="7" fill="#fbbf24" stroke="#ffffff" strokeWidth="2" />
                  <text x={vx} y={vy + 3} fill="#000000" fontSize="8" fontWeight="bold" textAnchor="middle">
                    🚑
                  </text>
                </g>
              );
            }

            return (
              <circle
                key={veh.vehicle_id}
                cx={vx}
                cy={vy}
                r="3.5"
                fill="#38bdf8"
                stroke="#0284c7"
                strokeWidth="1"
              />
            );
          })}

          {/* Render Intersections */}
          {network.intersections.map((node) => {
            const pos = NODE_POSITIONS[node.intersection_id];
            if (!pos) return null;

            const sig = signalMap.get(node.intersection_id);
            const isSelected = selectedIntersectionId === node.intersection_id;
            const isCorridorNode = activeCorridorNodeSet.has(node.intersection_id);

            const isGreenEW = sig?.current_phase === 'EW_GREEN';
            const phaseLabel = isGreenEW ? 'EW' : 'NS';

            return (
              <g
                key={node.intersection_id}
                onClick={() => onSelectIntersection(node.intersection_id)}
                className="cursor-pointer group"
              >
                {/* Corridor Highlight Circle */}
                {isCorridorNode && (
                  <circle
                    cx={pos.x}
                    cy={pos.y}
                    r="28"
                    fill="none"
                    stroke="#fbbf24"
                    strokeWidth="3"
                    strokeDasharray="4,2"
                    className="animate-spin-slow"
                  />
                )}

                {/* Selection Ring */}
                {isSelected && (
                  <circle cx={pos.x} cy={pos.y} r="26" fill="none" stroke="#38bdf8" strokeWidth="2" />
                )}

                {/* Node Main Circle */}
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r="20"
                  fill="#0f172a"
                  stroke={isCorridorNode ? '#fbbf24' : isSelected ? '#38bdf8' : '#334155'}
                  strokeWidth="2.5"
                  className="group-hover:stroke-cyan-400 transition-colors"
                />

                {/* Signal Light Color Indicator */}
                <circle
                  cx={pos.x - 10}
                  cy={pos.y - 10}
                  r="4"
                  fill={isGreenEW ? '#22c55e' : '#ef4444'}
                />

                {/* Node ID */}
                <text
                  x={pos.x}
                  y={pos.y + 4}
                  fill="#f8fafc"
                  fontSize="12"
                  fontWeight="bold"
                  textAnchor="middle"
                >
                  {node.intersection_id}
                </text>

                {/* Signal Phase Badge */}
                <rect
                  x={pos.x - 14}
                  y={pos.y + 24}
                  width="28"
                  height="14"
                  rx="3"
                  fill="#1e293b"
                  stroke="#475569"
                  strokeWidth="0.5"
                />
                <text
                  x={pos.x}
                  y={pos.y + 34}
                  fill={isGreenEW ? '#4ade80' : '#f87171'}
                  fontSize="9"
                  fontWeight="700"
                  textAnchor="middle"
                >
                  {phaseLabel}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
};
