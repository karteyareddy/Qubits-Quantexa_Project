'use client';

import React, { useState } from 'react';
import {
  EmergencyCorridorResponse,
  NetworkSchema,
  SignalStateSchema,
  SimulationStateSnapshot,
  VehicleStateSchema,
} from '../../lib/types';
import { CITY_INTERSECTIONS, ROAD_SIGN_NAMES } from '../../lib/cityMapConfig';
import { useTheme } from '../../context/ThemeContext';

interface TrafficMapProps {
  network: NetworkSchema | null;
  stateSnapshot: SimulationStateSnapshot | null;
  emergencyCorridors: EmergencyCorridorResponse[];
  selectedIntersectionId: string | null;
  onSelectIntersection: (id: string) => void;
}

export const TrafficMap: React.FC<TrafficMapProps> = ({
  network,
  stateSnapshot,
  emergencyCorridors,
  selectedIntersectionId,
  onSelectIntersection,
}) => {
  const { theme, toggleTheme } = useTheme();
  const [showHeadlights, setShowHeadlights] = useState<boolean>(true);
  const [hoveredVehicle, setHoveredVehicle] = useState<VehicleStateSchema | null>(null);
  const [zoomLevel, setZoomLevel] = useState<number>(1);

  const isLight = theme === 'light';

  if (!network) {
    return (
      <div className={`rounded-2xl p-12 text-center transition-all ${
        isLight ? 'bg-white text-slate-500 shadow-sm' : 'bg-slate-900 text-slate-400 shadow-md'
      }`}>
        <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        Loading City Traffic Digital Twin...
      </div>
    );
  }

  // Signal state lookup
  const signalMap = new Map<string, SignalStateSchema>();
  stateSnapshot?.signals?.forEach((s) => signalMap.set(s.intersection_id, s));

  // Edge state lookup
  const edgeStateMap = new Map<string, { count: number; isClosed: boolean; capacity: number; multiplier: number }>();
  stateSnapshot?.edges?.forEach((e) => {
    edgeStateMap.set(e.edge_id, {
      count: e.vehicle_count,
      isClosed: e.is_closed,
      capacity: e.capacity,
      multiplier: e.travel_time_multiplier,
    });
  });

  const activeEventMap = new Map(
    stateSnapshot?.active_events?.map((event) => [event.target, event]) ?? []
  );

  // Active emergency corridors
  const activeCorridor = emergencyCorridors.find(
    (c) => c.status.toLowerCase() === 'active' || c.status.toLowerCase() === 'planned'
  );

  const activeCorridorEdgeSet = new Set<string>();
  if (activeCorridor) {
    activeCorridor.route.forEach((eId) => activeCorridorEdgeSet.add(eId));
  }

  const activeCorridorNodeSet = new Set<string>(activeCorridor?.intersections || []);
  const activeVehiclesList = stateSnapshot?.vehicles.filter((v) => !v.has_arrived && v.current_edge_id) ?? [];
  const movingVehicleCount = activeVehiclesList.length;
  const emergencyCount = activeVehiclesList.filter((v) => v.is_emergency).length;

  return (
    <div className={`traffic-map-panel rounded-2xl shadow-xl relative overflow-hidden flex flex-col items-center transition-all duration-300 ${
      isLight ? 'bg-[#f4f3ef] text-slate-800' : 'bg-[#141b2d] text-slate-100'
    }`}>
      {/* 1. Sleek Modern Borderless Control Bar */}
      <div className="w-full px-5 py-2.5 z-20 flex items-center justify-between gap-4 pointer-events-auto bg-slate-900/40 backdrop-blur-md">
        {/* Left: Map Style & Feature Pills */}
        <div className="flex items-center space-x-2">
          <button
            onClick={toggleTheme}
            className="btn-map-pill"
            title="Toggle Map Style (Light / Dark)"
          >
            {isLight ? '☀️ Light Map' : '🌙 Night Map'}
          </button>

          {!isLight && (
            <button
              onClick={() => setShowHeadlights(!showHeadlights)}
              className="btn-map-pill"
            >
              💡 Headlights {showHeadlights ? 'On' : 'Off'}
            </button>
          )}

          <div className="hidden sm:flex items-center space-x-1.5 px-3 py-1.5 rounded-full text-xs font-medium text-slate-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>Live City Grid • 6 Signal Nodes</span>
          </div>
        </div>

        {/* Right: Live Telemetry Badges */}
        <div className="flex items-center space-x-2 shrink-0">
          <div className={`text-xs font-mono px-3.5 py-1.5 rounded-full font-semibold shadow-sm flex items-center space-x-2 ${
            isLight ? 'bg-white text-slate-700' : 'bg-slate-800/90 text-slate-200'
          }`}>
            <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
            <span>{movingVehicleCount} Moving Vehicles</span>
          </div>

          {emergencyCount > 0 && (
            <div className="text-xs font-mono px-3.5 py-1.5 rounded-full font-bold shadow-md bg-rose-500 text-white flex items-center space-x-1.5 animate-pulse">
              <span>🚑</span>
              <span>{emergencyCount} Emergency In Transit</span>
            </div>
          )}
        </div>
      </div>

      {/* 2. Floating Emergency Green Corridor Banner (glaringly visible alert) */}
      {activeCorridor && (
        <div className="w-full bg-gradient-to-r from-emerald-600 via-teal-500 to-emerald-600 text-white px-4 py-2 flex items-center justify-between text-xs font-bold shadow-lg z-20 animate-fade-in">
          <div className="flex items-center space-x-2">
            <span className="text-base animate-bounce">🚨</span>
            <span className="tracking-wide">EMERGENCY GREEN CORRIDOR ACTIVE:</span>
            <span className="bg-black/25 px-2.5 py-0.5 rounded-full font-mono text-emerald-100">
              {activeCorridor.intersections.join(' ➔ ')}
            </span>
          </div>
          <div className="flex items-center space-x-3 text-[11px] font-mono text-emerald-100">
            <span>Signals Preempted (Green Wave)</span>
            <span className="w-2 h-2 rounded-full bg-white animate-ping" />
          </div>
        </div>
      )}

      {/* 3. SVG Canvas Container */}
      <div className="w-full relative overflow-hidden flex justify-center select-none py-1">
        {/* Vehicle Hover Card HUD */}
        {hoveredVehicle && (
          <div className={`absolute top-4 left-4 z-30 rounded-2xl p-3.5 shadow-2xl text-xs backdrop-blur-xl pointer-events-none min-w-[220px] transition-all ${
            isLight ? 'bg-white/95 text-slate-800 shadow-slate-300/50' : 'bg-slate-900/95 text-slate-100 shadow-black/60'
          }`}>
            <div className="flex items-center justify-between pb-1.5 mb-2 border-b border-slate-200/60 dark:border-slate-800">
              <span className="font-bold font-mono flex items-center space-x-1.5 text-blue-500 dark:text-cyan-400">
                <span>{hoveredVehicle.is_emergency ? '🚑' : '🚗'}</span>
                <span>{hoveredVehicle.vehicle_id}</span>
              </span>
              <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase ${
                hoveredVehicle.is_emergency ? 'bg-rose-500 text-white' : 'bg-blue-500/20 text-blue-500 dark:text-cyan-300'
              }`}>
                {hoveredVehicle.is_emergency ? 'Emergency' : 'Standard'}
              </span>
            </div>
            <div className="space-y-1 text-[11px]">
              <div>Speed: <strong className="font-mono">{(hoveredVehicle.speed_mps * 3.6).toFixed(0)} km/h</strong></div>
              <div>Route: <span className="font-mono font-semibold">{hoveredVehicle.origin} → {hoveredVehicle.destination}</span></div>
              <div>Street: <span className="text-slate-500 dark:text-slate-400">{ROAD_SIGN_NAMES[hoveredVehicle.current_edge_id || '']?.name || hoveredVehicle.current_edge_id}</span></div>
            </div>
          </div>
        )}

        {/* Bottom-Right Zoom & Reset Controls (borderless pills) */}
        <div className="absolute bottom-4 right-4 z-20 flex flex-col items-end space-y-2 pointer-events-auto">
          <div className={`flex flex-col rounded-2xl shadow-lg overflow-hidden backdrop-blur-md ${
            isLight ? 'bg-white/90' : 'bg-slate-900/90'
          }`}>
            <button
              onClick={() => setZoomLevel((z) => Math.min(1.3, z + 0.1))}
              className="px-3 py-1.5 text-slate-700 dark:text-slate-200 hover:bg-slate-200/50 dark:hover:bg-slate-800 font-bold text-sm transition-all"
              title="Zoom In"
            >
              +
            </button>
            <button
              onClick={() => setZoomLevel((z) => Math.max(0.8, z - 0.1))}
              className="px-3 py-1.5 text-slate-700 dark:text-slate-200 hover:bg-slate-200/50 dark:hover:bg-slate-800 font-bold text-sm transition-all"
              title="Zoom Out"
            >
              −
            </button>
          </div>

          <button
            onClick={() => setZoomLevel(1)}
            className="btn-map-pill"
            title="Reset Map Zoom"
          >
            Reset View
          </button>
        </div>

        {/* 4. Main SVG Vector Map */}
        <svg
          viewBox="0 0 880 460"
          preserveAspectRatio="xMidYMid meet"
          className="w-full max-w-[1040px] transition-transform duration-300"
          style={{ transform: `scale(${zoomLevel})`, transformOrigin: 'center center' }}
        >
          <defs>
            {/* Emerald Glow Filter for Emergency Corridor */}
            <filter id="corridor-glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="6" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>

            {/* Subtle Water Gradient */}
            <linearGradient id="gmap-water" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor={isLight ? '#bfdbfe' : '#1e3a5f'} />
              <stop offset="100%" stopColor={isLight ? '#93c5fd' : '#0f2744'} />
            </linearGradient>

            {/* Lush Park Gradient */}
            <linearGradient id="gmap-park" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor={isLight ? '#dcfce7' : '#14382c'} />
              <stop offset="100%" stopColor={isLight ? '#bbf7d0' : '#0d2820'} />
            </linearGradient>

            {/* Urban District Block Fill */}
            <pattern id="gmap-block" width="30" height="30" patternUnits="userSpaceOnUse">
              <rect width="30" height="30" fill={isLight ? '#edeae4' : '#1c2438'} />
              <rect x="2" y="2" width="12" height="12" rx="2" fill={isLight ? '#e5e1d8' : '#232e44'} />
              <rect x="16" y="2" width="12" height="12" rx="2" fill={isLight ? '#e5e1d8' : '#232e44'} />
              <rect x="2" y="16" width="12" height="12" rx="2" fill={isLight ? '#e5e1d8' : '#232e44'} />
              <rect x="16" y="16" width="12" height="12" rx="2" fill={isLight ? '#e5e1d8' : '#232e44'} />
            </pattern>

            {/* Car Headlight Beam */}
            <linearGradient id="gmap-headlight-beam" x1="0%" y1="50%" x2="100%" y2="50%">
              <stop offset="0%" stopColor="#fef08a" stopOpacity="0.85" />
              <stop offset="100%" stopColor="#fef08a" stopOpacity="0" />
            </linearGradient>

            {/* Directional Arrows */}
            <marker id="corridor-arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1 L 10 5 L 0 9 z" fill="#10b981" />
            </marker>
            <marker id="gmap-arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="5" markerHeight="5" orient="auto">
              <path d="M 0 1 L 10 5 L 0 9 z" fill={isLight ? '#2563eb' : '#38bdf8'} />
            </marker>
          </defs>

          {/* Background Canvas */}
          <rect width="880" height="460" fill={isLight ? '#f4f3ef' : '#141b2d'} />

          {/* Urban Districts Background Grids */}
          <g className="gmap-districts pointer-events-none">
            {/* Northwest District */}
            <rect x="20" y="15" width="220" height="70" rx="8" fill="url(#gmap-block)" />
            <text x="130" y="52" fill={isLight ? '#64748b' : '#94a3b8'} fontSize="8" fontWeight="700" textAnchor="middle" letterSpacing="1">
              NORTHWEST TRANSIT DISTRICT
            </text>

            {/* Southwest District */}
            <rect x="20" y="380" width="220" height="65" rx="8" fill="url(#gmap-block)" />
            <text x="130" y="415" fill={isLight ? '#64748b' : '#94a3b8'} fontSize="8" fontWeight="700" textAnchor="middle" letterSpacing="1">
              INNOVATION TECH DISTRICT
            </text>

            {/* Northeast District */}
            <rect x="480" y="15" width="280" height="70" rx="8" fill="url(#gmap-block)" />
            <text x="620" y="52" fill={isLight ? '#64748b' : '#94a3b8'} fontSize="8" fontWeight="700" textAnchor="middle" letterSpacing="1">
              CIVIC & COMMERCIAL DISTRICT
            </text>

            {/* Southeast District */}
            <rect x="480" y="380" width="280" height="65" rx="8" fill="url(#gmap-block)" />
            <text x="620" y="415" fill={isLight ? '#64748b' : '#94a3b8'} fontSize="8" fontWeight="700" textAnchor="middle" letterSpacing="1">
              METROPOLITAN MARKET CORE
            </text>
          </g>

          {/* Natural Water Body: Emerald Bay (Clean West Lake) */}
          <g className="gmap-water-bodies pointer-events-none">
            <path
              d="M 185 180 C 205 160, 245 165, 275 185 C 315 210, 320 260, 290 290 C 250 320, 205 310, 185 280 C 165 250, 170 200, 185 180 Z"
              fill="url(#gmap-water)"
              opacity="0.85"
            />
            <text
              x="245"
              y="238"
              fill={isLight ? '#1e40af' : '#93c5fd'}
              fontSize="9"
              fontWeight="700"
              textAnchor="middle"
              letterSpacing="0.5"
            >
              Emerald Bay Lake
            </text>
          </g>

          {/* Parks & Conservatories */}
          <g className="gmap-parks pointer-events-none">
            <rect x="335" y="160" width="70" height="140" rx="8" fill="url(#gmap-park)" opacity="0.85" />
            <text x="370" y="235" fill={isLight ? '#166534' : '#86efac'} fontSize="8" fontWeight="700" textAnchor="middle">
              CIVIC PARK
            </text>

            <rect x="470" y="160" width="235" height="140" rx="8" fill="url(#gmap-park)" opacity="0.85" />
            <text x="587" y="235" fill={isLight ? '#166534' : '#86efac'} fontSize="8.5" fontWeight="700" textAnchor="middle" letterSpacing="0.5">
              METROPOLITAN CENTRAL PARK
            </text>
          </g>

          {/* Eastern Bay Harbor Port */}
          <g className="gmap-east-water pointer-events-none">
            <rect x="785" y="0" width="95" height="460" fill="url(#gmap-water)" opacity="0.9" />
            <text
              x="832"
              y="235"
              fill={isLight ? '#1e40af' : '#93c5fd'}
              fontSize="9.5"
              fontWeight="800"
              textAnchor="middle"
              letterSpacing="1"
            >
              BAY HARBOR
            </text>
          </g>

          {/* Minor Connecting Streets Grid */}
          <g className="gmap-minor-roads pointer-events-none" stroke={isLight ? '#e2e8f0' : '#243048'} strokeWidth="5" strokeLinecap="round">
            <line x1="30" y1="230" x2="135" y2="230" />
            <line x1="135" y1="230" x2="180" y2="230" />
            <line x1="435" y1="230" x2="470" y2="230" />
            <line x1="705" y1="230" x2="735" y2="230" />
            <line x1="285" y1="20" x2="285" y2="110" />
            <line x1="585" y1="20" x2="585" y2="110" />
            <line x1="285" y1="350" x2="285" y2="440" />
            <line x1="585" y1="350" x2="585" y2="440" />
          </g>

          {/* Arterial Road Network */}
          <g className="gmap-arterial-roads">
            {network.edges.map((edge) => {
              const src = CITY_INTERSECTIONS[edge.source_intersection];
              const tgt = CITY_INTERSECTIONS[edge.target_intersection];
              if (!src || !tgt) return null;

              const edgeInfo = edgeStateMap.get(edge.edge_id) || {
                count: 0,
                isClosed: false,
                capacity: edge.capacity,
                multiplier: 1,
              };

              const isCorridorEdge = activeCorridorEdgeSet.has(edge.edge_id);
              const activeEvent = activeEventMap.get(edge.edge_id);
              const isIncident = Boolean(activeEvent);

              // Directional offset for opposing lanes
              const dx = tgt.x - src.x;
              const dy = tgt.y - src.y;
              const len = Math.sqrt(dx * dx + dy * dy);
              const offsetX = (-dy / len) * 7.5;
              const offsetY = (dx / len) * 7.5;

              const x1 = src.x + offsetX;
              const y1 = src.y + offsetY;
              const x2 = tgt.x + offsetX;
              const y2 = tgt.y + offsetY;

              // Road styling
              const roadCasingColor = isLight ? '#cbd5e1' : '#1e293b';
              let laneFlowColor = isLight ? '#2563eb' : '#38bdf8';

              if (edgeInfo.isClosed) {
                laneFlowColor = '#ef4444';
              } else if (edgeInfo.count >= 8) {
                laneFlowColor = '#dc2626';
              } else if (edgeInfo.count >= 3) {
                laneFlowColor = '#f59e0b';
              }

              return (
                <g key={`gmap-road-${edge.edge_id}`}>
                  {/* Outer Road Bed */}
                  <line
                    x1={src.x}
                    y1={src.y}
                    x2={tgt.x}
                    y2={tgt.y}
                    stroke={roadCasingColor}
                    strokeWidth={24}
                    strokeLinecap="round"
                  />

                  {/* Asphalt Pavement */}
                  <line
                    x1={src.x}
                    y1={src.y}
                    x2={tgt.x}
                    y2={tgt.y}
                    stroke={isLight ? '#ffffff' : '#232d3f'}
                    strokeWidth={20}
                    strokeLinecap="round"
                  />

                  {/* Yellow Center Divider */}
                  <line
                    x1={src.x}
                    y1={src.y}
                    x2={tgt.x}
                    y2={tgt.y}
                    stroke="#eab308"
                    strokeWidth={1.5}
                    strokeOpacity={0.8}
                  />

                  {/* Normal Flow Lane Direction Marker */}
                  {!isCorridorEdge && (
                    <line
                      x1={x1}
                      y1={y1}
                      x2={x2}
                      y2={y2}
                      stroke={laneFlowColor}
                      strokeWidth={edgeInfo.isClosed ? 3.5 : 2.5}
                      strokeDasharray={edgeInfo.isClosed ? '5,4' : '8,10'}
                      markerEnd="url(#gmap-arrow-blue)"
                    />
                  )}

                  {/* Incident Alert Badge */}
                  {isIncident && (
                    <g transform={`translate(${(x1 + x2) / 2}, ${(y1 + y2) / 2})`}>
                      <circle r="11" fill="#ef4444" stroke="#ffffff" strokeWidth="2" className="animate-pulse" />
                      <text y="3.5" fill="#fff" fontSize="9" fontWeight="bold" textAnchor="middle">
                        !
                      </text>
                    </g>
                  )}

                  {/* Vehicle Count Pill */}
                  <g transform={`translate(${(x1 + x2) / 2 + (offsetX > 0 ? 8 : -8)}, ${(y1 + y2) / 2 + (offsetY > 0 ? 8 : -8)})`}>
                    <rect
                      x="-12"
                      y="-6"
                      width="24"
                      height="12"
                      rx="4"
                      fill={isLight ? '#ffffff' : '#0f172a'}
                      stroke={edgeInfo.isClosed ? '#ef4444' : edgeInfo.count > 5 ? '#dc2626' : isLight ? '#cbd5e1' : '#334155'}
                      strokeWidth="1"
                      className="shadow-sm"
                    />
                    <text
                      x="0"
                      y="3"
                      fill={edgeInfo.isClosed ? '#dc2626' : edgeInfo.count > 5 ? '#ef4444' : isLight ? '#475569' : '#94a3b8'}
                      fontSize="8"
                      fontWeight="700"
                      textAnchor="middle"
                      fontFamily="monospace"
                    >
                      {edgeInfo.isClosed ? '✕' : `${edgeInfo.count}v`}
                    </text>
                  </g>
                </g>
              );
            })}
          </g>

          {/* 5. RADIANT EMERGENCY GREEN CORRIDOR OVERLAY (GLARINGLY VISIBLE) */}
          {activeCorridor && (
            <g className="emergency-corridor-overlay pointer-events-none">
              {activeCorridor.route.map((edgeId) => {
                const edge = network.edges.find((e) => e.edge_id === edgeId);
                if (!edge) return null;
                const src = CITY_INTERSECTIONS[edge.source_intersection];
                const tgt = CITY_INTERSECTIONS[edge.target_intersection];
                if (!src || !tgt) return null;

                const dx = tgt.x - src.x;
                const dy = tgt.y - src.y;
                const len = Math.sqrt(dx * dx + dy * dy);
                const laneOffsetX = (-dy / len) * 7.5;
                const laneOffsetY = (dx / len) * 7.5;

                const x1 = src.x + laneOffsetX;
                const y1 = src.y + laneOffsetY;
                const x2 = tgt.x + laneOffsetX;
                const y2 = tgt.y + laneOffsetY;

                return (
                  <g key={`corridor-path-${edgeId}`}>
                    {/* Glowing Emerald Aura Underlay */}
                    <line
                      x1={x1}
                      y1={y1}
                      x2={x2}
                      y2={y2}
                      stroke="#10b981"
                      strokeWidth={22}
                      strokeOpacity={0.4}
                      strokeLinecap="round"
                      filter="url(#corridor-glow)"
                    />

                    {/* Solid Vivid Emerald Ribbon */}
                    <line
                      x1={x1}
                      y1={y1}
                      x2={x2}
                      y2={y2}
                      stroke="#059669"
                      strokeWidth={13}
                      strokeLinecap="round"
                    />

                    {/* Animated Flowing Neon Green Center Beam with Arrows */}
                    <line
                      x1={x1}
                      y1={y1}
                      x2={x2}
                      y2={y2}
                      stroke="#34d399"
                      strokeWidth={4}
                      strokeDasharray="14,10"
                      className="animate-corridor-flow"
                      markerEnd="url(#corridor-arrow)"
                    />
                  </g>
                );
              })}
            </g>
          )}

          {/* 6. Clean Highway Shields & Road Signage (Human Metropolitan Names) */}
          <g className="gmap-road-labels pointer-events-none">
            {/* Grand Parkway Route 10 (North Arterial) */}
            <g transform="translate(285, 84)">
              <text x="0" y="0" fill={isLight ? '#1e293b' : '#f8fafc'} fontSize="8.5" fontWeight="700" textAnchor="middle">
                Grand Parkway (Route 10)
              </text>
            </g>
            <g transform="translate(285, 110)">
              <rect x="-18" y="-6.5" width="36" height="13" rx="3" fill="#0284c7" />
              <text x="0" y="3.5" fill="#ffffff" fontSize="7.5" fontWeight="800" textAnchor="middle">
                RT 10
              </text>
            </g>

            <g transform="translate(585, 84)">
              <text x="0" y="0" fill={isLight ? '#1e293b' : '#f8fafc'} fontSize="8.5" fontWeight="700" textAnchor="middle">
                Grand Parkway (Route 10)
              </text>
            </g>
            <g transform="translate(585, 110)">
              <rect x="-18" y="-6.5" width="36" height="13" rx="3" fill="#0284c7" />
              <text x="0" y="3.5" fill="#ffffff" fontSize="7.5" fontWeight="800" textAnchor="middle">
                RT 10
              </text>
            </g>

            {/* Ocean Boulevard Route 20 (South Arterial) */}
            <g transform="translate(285, 332)">
              <text x="0" y="0" fill={isLight ? '#1e293b' : '#f8fafc'} fontSize="8.5" fontWeight="700" textAnchor="middle">
                Ocean Boulevard (Route 20)
              </text>
            </g>
            <g transform="translate(285, 350)">
              <rect x="-18" y="-6.5" width="36" height="13" rx="3" fill="#0284c7" />
              <text x="0" y="3.5" fill="#ffffff" fontSize="7.5" fontWeight="800" textAnchor="middle">
                RT 20
              </text>
            </g>

            <g transform="translate(585, 332)">
              <text x="0" y="0" fill={isLight ? '#1e293b' : '#f8fafc'} fontSize="8.5" fontWeight="700" textAnchor="middle">
                Ocean Boulevard (Route 20)
              </text>
            </g>
            <g transform="translate(585, 350)">
              <rect x="-18" y="-6.5" width="36" height="13" rx="3" fill="#0284c7" />
              <text x="0" y="3.5" fill="#ffffff" fontSize="7.5" fontWeight="800" textAnchor="middle">
                RT 20
              </text>
            </g>

            {/* North-South Vertical Avenues */}
            <g transform="translate(118, 230) rotate(-90)">
              <text x="0" y="3" fill={isLight ? '#475569' : '#94a3b8'} fontSize="8" fontWeight="700" textAnchor="middle">
                1ST AVENUE NORTH
              </text>
            </g>

            <g transform="translate(418, 230) rotate(-90)">
              <text x="0" y="3" fill={isLight ? '#475569' : '#94a3b8'} fontSize="8" fontWeight="700" textAnchor="middle">
                BROADWAY AVENUE
              </text>
            </g>

            <g transform="translate(718, 230) rotate(-90)">
              <text x="0" y="3" fill={isLight ? '#475569' : '#94a3b8'} fontSize="8" fontWeight="700" textAnchor="middle">
                HARBOR EXPRESSWAY (I-95)
              </text>
            </g>
          </g>

          {/* 7. Pedestrian Crosswalks */}
          <g className="gmap-crosswalks opacity-80 pointer-events-none">
            {Object.values(CITY_INTERSECTIONS).map((node) => (
              <g key={`crosswalk-${node.id}`}>
                <rect x={node.x - 16} y={node.y - 28} width="32" height="7" fill={isLight ? '#cbd5e1' : '#475569'} />
                <rect x={node.x - 16} y={node.y + 21} width="32" height="7" fill={isLight ? '#cbd5e1' : '#475569'} />
                <rect x={node.x - 28} y={node.y - 16} width="7" height="32" fill={isLight ? '#cbd5e1' : '#475569'} />
                <rect x={node.x + 21} y={node.y - 16} width="7" height="32" fill={isLight ? '#cbd5e1' : '#475569'} />
              </g>
            ))}
          </g>

          {/* 8. Moving Realistic Vehicles */}
          <g className="gmap-vehicles">
            {activeVehiclesList.map((veh, idx) => {
              const edge = network.edges.find((e) => e.edge_id === veh.current_edge_id);
              if (!edge) return null;

              const src = CITY_INTERSECTIONS[edge.source_intersection];
              const tgt = CITY_INTERSECTIONS[edge.target_intersection];
              if (!src || !tgt) return null;

              // Lane offset
              const dx = tgt.x - src.x;
              const dy = tgt.y - src.y;
              const len = Math.sqrt(dx * dx + dy * dy);
              const laneOffsetX = (-dy / len) * 7.5;
              const laneOffsetY = (dx / len) * 7.5;

              // Angle & Position
              const angleDeg = (Math.atan2(dy, dx) * 180) / Math.PI;
              const ratio = Math.min(1.0, Math.max(0.0, veh.distance_on_current_edge_meters / edge.length_meters));
              const vx = src.x + laneOffsetX + (tgt.x - src.x) * ratio;
              const vy = src.y + laneOffsetY + (tgt.y - src.y) * ratio;

              // Colors
              const carColor = isLight ? (idx % 2 === 0 ? '#2563eb' : '#0891b2') : (idx % 2 === 0 ? '#38bdf8' : '#06b6d4');

              if (veh.is_emergency) {
                // Emergency Ambulance with high-visibility siren pulses
                return (
                  <g
                    key={veh.vehicle_id}
                    transform={`translate(${vx}, ${vy})`}
                    className="cursor-pointer group"
                    onMouseEnter={() => setHoveredVehicle(veh)}
                    onMouseLeave={() => setHoveredVehicle(null)}
                  >
                    {/* Radiating beacon rings */}
                    <circle cx="0" cy="0" r="26" fill="none" stroke="#ef4444" strokeWidth="2.5" className="animate-ping" />
                    <circle cx="0" cy="0" r="18" fill="none" stroke="#10b981" strokeWidth="2" opacity="0.75" />

                    {/* Vehicle body rotated along heading */}
                    <g transform={`rotate(${angleDeg})`}>
                      {!isLight && showHeadlights && (
                        <polygon points="14,-5 60,-18 60,18 14,5" fill="url(#gmap-headlight-beam)" opacity={0.8} />
                      )}

                      <rect x="-14" y="-8" width="28" height="16" rx="4" fill="#ffffff" stroke="#dc2626" strokeWidth="2" className="shadow-lg" />
                      <rect x="-8" y="-7.5" width="16" height="3" fill="#dc2626" />
                      <rect x="-8" y="4.5" width="16" height="3" fill="#dc2626" />
                      {/* Red cross */}
                      <rect x="-3" y="-1.5" width="6" height="3" fill="#dc2626" />
                      <rect x="-1.5" y="-3" width="3" height="6" fill="#dc2626" />
                      {/* Windshield */}
                      <path d="M 6 -6 L 9 -5 L 9 5 L 6 6 Z" fill="#1e293b" />
                      {/* Dual Flashing Emergency Lights */}
                      <circle cx="0" cy="-3.5" r="3" fill="#ef4444" className="animate-pulse" />
                      <circle cx="0" cy="3.5" r="3" fill="#3b82f6" className="animate-pulse" />
                    </g>

                    {/* EMS Label Badge */}
                    <g transform="translate(0, -18)">
                      <rect x="-18" y="-6" width="36" height="12" rx="3" fill="#ef4444" className="shadow-md" />
                      <text x="0" y="3" fill="#ffffff" fontSize="7.5" fontWeight="900" textAnchor="middle">
                        EMS-911
                      </text>
                    </g>
                  </g>
                );
              }

              // Standard Passenger Car
              return (
                <g
                  key={veh.vehicle_id}
                  transform={`translate(${vx}, ${vy}) rotate(${angleDeg})`}
                  className="cursor-pointer group"
                  onMouseEnter={() => setHoveredVehicle(veh)}
                  onMouseLeave={() => setHoveredVehicle(null)}
                >
                  {!isLight && showHeadlights && (
                    <polygon points="11,-4.5 45,-14 45,14 11,4.5" fill="url(#gmap-headlight-beam)" opacity={0.6} />
                  )}

                  <rect x="-10" y="-5" width="20" height="10" rx="3" fill="#000000" opacity={0.25} />
                  <rect x="-9.5" y="-4.5" width="19" height="9" rx="2.5" fill={carColor} stroke="#1e293b" strokeWidth="0.8" />
                  <path d="M 3.5 -3 L 6 -2.2 L 6 2.2 L 3.5 3 Z" fill="#1e293b" />
                  <circle cx="9" cy="-3" r="1" fill="#fef08a" />
                  <circle cx="9" cy="3" r="1" fill="#fef08a" />
                </g>
              );
            })}
          </g>

          {/* 9. Intersections & Signal Nodes (Clean, Perfectly Aligned) */}
          <g className="gmap-intersections">
            {Object.values(CITY_INTERSECTIONS).map((node) => {
              const sig = signalMap.get(node.id);
              const isSelected = selectedIntersectionId === node.id;
              const isCorridorNode = activeCorridorNodeSet.has(node.id);

              const isGreenEW = sig?.current_phase === 'EW_GREEN';
              const phaseLabel = isGreenEW ? 'EW GREEN' : 'NS GREEN';

              return (
                <g
                  key={`node-${node.id}`}
                  onClick={() => onSelectIntersection(node.id)}
                  className="cursor-pointer group"
                >
                  <title>{`${node.name} (${node.code}): Click for signal timings`}</title>

                  {/* Synchronized Green Wave Halo for Active Corridor Nodes */}
                  {isCorridorNode && (
                    <>
                      <circle
                        cx={node.x}
                        cy={node.y}
                        r="32"
                        fill="none"
                        stroke="#10b981"
                        strokeWidth="3"
                        strokeOpacity="0.6"
                        className="animate-ping"
                      />
                      <circle
                        cx={node.x}
                        cy={node.y}
                        r="28"
                        fill="none"
                        stroke="#10b981"
                        strokeWidth="2.5"
                      />
                    </>
                  )}

                  {/* Selection Indicator Ring */}
                  {isSelected && (
                    <circle
                      cx={node.x}
                      cy={node.y}
                      r="29"
                      fill="none"
                      stroke={isLight ? '#2563eb' : '#38bdf8'}
                      strokeWidth="2.5"
                      className="animate-pulse"
                    />
                  )}

                  {/* Intersection Node Base Circle */}
                  <circle
                    cx={node.x}
                    cy={node.y}
                    r="22"
                    fill={isLight ? '#ffffff' : '#1e293b'}
                    stroke={isCorridorNode ? '#10b981' : isSelected ? '#38bdf8' : isLight ? '#94a3b8' : '#475569'}
                    strokeWidth="2.5"
                    className="shadow-md transition-all duration-200 group-hover:scale-110"
                  />

                  {/* Traffic Signal Lights (Clean 4-way LED optics) */}
                  <g transform={`translate(${node.x - 12}, ${node.y - 10})`}>
                    <rect x="0" y="0" width="7" height="12" rx="1.5" fill="#1e293b" />
                    <circle cx="3.5" cy="3.5" r="2" fill={isGreenEW ? '#374151' : '#ef4444'} />
                    <circle cx="3.5" cy="8.5" r="2" fill={isGreenEW ? '#22c55e' : '#374151'} />
                  </g>
                  <g transform={`translate(${node.x + 5}, ${node.y - 10})`}>
                    <rect x="0" y="0" width="7" height="12" rx="1.5" fill="#1e293b" />
                    <circle cx="3.5" cy="3.5" r="2" fill={isGreenEW ? '#374151' : '#ef4444'} />
                    <circle cx="3.5" cy="8.5" r="2" fill={isGreenEW ? '#22c55e' : '#374151'} />
                  </g>
                  <g transform={`translate(${node.x - 12}, ${node.y + 3})`}>
                    <rect x="0" y="0" width="7" height="12" rx="1.5" fill="#1e293b" />
                    <circle cx="3.5" cy="3.5" r="2" fill={!isGreenEW ? '#374151' : '#ef4444'} />
                    <circle cx="3.5" cy="8.5" r="2" fill={!isGreenEW ? '#22c55e' : '#374151'} />
                  </g>
                  <g transform={`translate(${node.x + 5}, ${node.y + 3})`}>
                    <rect x="0" y="0" width="7" height="12" rx="1.5" fill="#1e293b" />
                    <circle cx="3.5" cy="3.5" r="2" fill={!isGreenEW ? '#374151' : '#ef4444'} />
                    <circle cx="3.5" cy="8.5" r="2" fill={!isGreenEW ? '#22c55e' : '#374151'} />
                  </g>

                  {/* Center Node ID Badge */}
                  <circle
                    cx={node.x}
                    cy={node.y}
                    r="9"
                    fill={isCorridorNode ? '#059669' : isLight ? '#2563eb' : '#0284c7'}
                    stroke="#ffffff"
                    strokeWidth="1.2"
                  />
                  <text x={node.x} y={node.y + 3} fill="#ffffff" fontSize="9" fontWeight="900" textAnchor="middle">
                    {node.code}
                  </text>

                  {/* Clean Plaque Card Below Intersection */}
                  <g transform={`translate(${node.x}, ${node.y + 36})`}>
                    <rect
                      x="-65"
                      y="-11"
                      width="130"
                      height="22"
                      rx="6"
                      fill={isLight ? '#ffffff' : '#0f172a'}
                      stroke={isCorridorNode ? '#10b981' : isLight ? '#e2e8f0' : '#334155'}
                      strokeWidth={isCorridorNode ? 1.5 : 1}
                      className="shadow-md"
                    />
                    <text
                      x="0"
                      y="1"
                      fill={isLight ? '#0f172a' : '#ffffff'}
                      fontSize="8.5"
                      fontWeight="700"
                      textAnchor="middle"
                    >
                      {node.name}
                    </text>
                    <text
                      x="0"
                      y="8.5"
                      fill={isCorridorNode ? '#059669' : isLight ? '#2563eb' : '#38bdf8'}
                      fontSize="6.5"
                      fontWeight="700"
                      textAnchor="middle"
                    >
                      {isCorridorNode ? 'PRIORITY GREEN' : `${node.district} • ${phaseLabel}`}
                    </text>
                  </g>
                </g>
              );
            })}
          </g>
        </svg>
      </div>
    </div>
  );
};
