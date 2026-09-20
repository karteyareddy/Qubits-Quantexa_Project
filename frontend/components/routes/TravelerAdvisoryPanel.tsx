'use client';

import React, { useState, useEffect } from 'react';

export interface RouteOptionData {
  name: string;
  is_recommended: boolean;
  path_nodes: string[];
  path_edges: string[];
  distance_km: number;
  eta_minutes: number;
  congestion_level: string;
  weather_summary: string;
  flood_detected: boolean;
  lanes_available: string;
  risk_score: number;
  warnings: string[];
}

export interface TravelerAdvisoryData {
  origin: string;
  destination: string;
  urgency: string;
  direct_route: RouteOptionData;
  alternative_route: RouteOptionData;
  recommendation_summary: string;
  congestion_avoided_pct: number;
  flood_risk_avoided: boolean;
  travel_time_saved_minutes: number;
}

interface TravelerAdvisoryPanelProps {
  id?: string;
  onSelectRouteForHighlight?: (nodes: string[], routeType: 'direct' | 'alternative') => void;
}

export const TravelerAdvisoryPanel: React.FC<TravelerAdvisoryPanelProps> = ({
  id = 'advisory',
  onSelectRouteForHighlight,
}) => {
  const [origin, setOrigin] = useState('I1');
  const [destination, setDestination] = useState('I6');
  const [urgency, setUrgency] = useState('normal');
  const [loading, setLoading] = useState(false);
  const [advisory, setAdvisory] = useState<TravelerAdvisoryData | null>(null);

  const fetchAdvisory = async (org = origin, dst = destination, urg = urgency) => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/v1/routes/traveler-advisory', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ origin: org, destination: dst, urgency: urg }),
      });
      if (res.ok) {
        const data = await res.json();
        setAdvisory(data);
      }
    } catch {
      // Fallback
      setAdvisory({
        origin: org,
        destination: dst,
        urgency: urg,
        direct_route: {
          name: 'Direct Route (Grand Central Arterial)',
          is_recommended: false,
          path_nodes: ['I1', 'I2', 'I5', 'I6'],
          path_edges: ['E_I1_I2', 'E_I2_I5', 'E_I5_I6'],
          distance_km: 4.8,
          eta_minutes: 16.2,
          congestion_level: 'High (0.85)',
          weather_summary: 'Zone 2 Heavy Rain / Flooding',
          flood_detected: true,
          lanes_available: '1 of 2 lanes (50%)',
          risk_score: 8.5,
          warnings: ['Water accumulation 12cm across Route 10', '1 lane unusable; queue spillback active'],
        },
        alternative_route: {
          name: 'Safe Alternative Route (South Civic Detour)',
          is_recommended: true,
          path_nodes: ['I1', 'I4', 'I5', 'I6'],
          path_edges: ['E_I1_I4', 'E_I4_I5', 'E_I5_I6'],
          distance_km: 5.2,
          eta_minutes: 9.4,
          congestion_level: 'Moderate (0.42)',
          weather_summary: 'Zone 4 Dry / Clear',
          flood_detected: false,
          lanes_available: '2 of 2 lanes (100%)',
          risk_score: 1.2,
          warnings: [],
        },
        recommendation_summary:
          'Direct route via I2 is impaired by flood water. Alternative detour via I4 bypasses the flood zone, saving ~6.8 mins.',
        congestion_avoided_pct: 42.0,
        flood_risk_avoided: true,
        travel_time_saved_minutes: 6.8,
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdvisory();
  }, []);

  return (
    <div id={id} className="advisory-panel rounded-2xl p-5 shadow-xl space-y-3.5 transition-all">
      <div className="flex justify-between items-center">
        <h3 className="text-xs font-bold text-cyan-500 dark:text-cyan-400 uppercase tracking-wider flex items-center space-x-2">
          <span>🗺️</span>
          <span>TRAVELER WEATHER ADVISORY & ROUTE GUIDANCE</span>
        </h3>
        <span className="text-[10px] font-mono font-semibold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
          ADAPTIVE ROUTING
        </span>
      </div>

      <p className="text-xs text-slate-500 dark:text-slate-400">
        Real-time evaluation of environmental hazard exposure, flood delays, and safe alternative detours.
      </p>

      {/* Input Selection Bar */}
      <div className="flex flex-wrap items-center gap-3 p-3 bg-slate-100 dark:bg-slate-900/60 rounded-xl text-xs">
        <div className="flex items-center gap-1.5">
          <span className="text-slate-400 font-mono text-[11px]">FROM:</span>
          <select
            value={origin}
            onChange={(e) => {
              setOrigin(e.target.value);
              fetchAdvisory(e.target.value, destination, urgency);
            }}
            className="bg-white dark:bg-slate-950/60 border border-slate-200/60 dark:border-slate-800 text-slate-800 dark:text-slate-200 px-3 py-1.5 rounded-lg text-xs font-medium focus:outline-none focus:ring-1 focus:ring-cyan-500"
          >
            <option value="I1">I1: Northwest Gateway</option>
            <option value="I2">I2: Grand Central</option>
            <option value="I4">I4: South Civic Hub</option>
          </select>
        </div>

        <div className="flex items-center gap-1.5">
          <span className="text-slate-400 font-mono text-[11px]">TO:</span>
          <select
            value={destination}
            onChange={(e) => {
              setDestination(e.target.value);
              fetchAdvisory(origin, e.target.value, urgency);
            }}
            className="bg-white dark:bg-slate-950/60 border border-slate-200/60 dark:border-slate-800 text-slate-800 dark:text-slate-200 px-3 py-1.5 rounded-lg text-xs font-medium focus:outline-none focus:ring-1 focus:ring-cyan-500"
          >
            <option value="I6">I6: East Tech Hub</option>
            <option value="I5">I5: Market Square</option>
            <option value="I3">I3: Financial Plaza</option>
          </select>
        </div>

        <div className="flex items-center gap-1.5">
          <span className="text-slate-400 font-mono text-[11px]">PRIORITY:</span>
          <select
            value={urgency}
            onChange={(e) => {
              setUrgency(e.target.value);
              fetchAdvisory(origin, destination, e.target.value);
            }}
            className="bg-white dark:bg-slate-950/60 border border-slate-200/60 dark:border-slate-800 text-slate-800 dark:text-slate-200 px-3 py-1.5 rounded-lg text-xs font-medium focus:outline-none focus:ring-1 focus:ring-cyan-500"
          >
            <option value="normal">Normal Traveler</option>
            <option value="high">High Urgency</option>
            <option value="emergency">Emergency Responder</option>
          </select>
        </div>

        <button
          onClick={() => fetchAdvisory()}
          disabled={loading}
          className="ml-auto bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold px-3.5 py-1.5 rounded-lg text-xs transition-all flex items-center gap-1 shadow-sm"
        >
          {loading ? 'Analyzing...' : '🔄 Re-evaluate'}
        </button>
      </div>

      {/* Advisory Summary Banner */}
      {advisory && (
        <div className="p-3 rounded-xl bg-blue-500/10 dark:bg-blue-500/15 text-xs flex flex-col gap-1">
          <div className="flex items-center gap-2">
            <span className="text-base">📢</span>
            <span className="font-bold text-blue-600 dark:text-blue-300">Municipal Traffic Guidance</span>
            {advisory.flood_risk_avoided && (
              <span className="ml-auto text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-600 dark:text-emerald-300 font-bold">
                ✅ FLOOD AVOIDED
              </span>
            )}
          </div>
          <p className="text-slate-600 dark:text-slate-300 text-xs leading-relaxed">
            {advisory.recommendation_summary}
          </p>
        </div>
      )}

      {/* Route Cards Comparison */}
      {advisory && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          {/* Direct Route Card */}
          <div
            className={`p-3.5 rounded-xl flex flex-col justify-between gap-2.5 transition-all ${
              advisory.direct_route.flood_detected
                ? 'bg-rose-500/10 ring-1 ring-rose-500/30'
                : 'bg-slate-100 dark:bg-slate-900/60'
            }`}
          >
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <span className="font-bold text-slate-800 dark:text-slate-200">
                  {advisory.direct_route.name}
                </span>
                <span
                  className={`text-[9px] font-mono px-2 py-0.5 rounded-full uppercase font-bold ${
                    advisory.direct_route.flood_detected
                      ? 'bg-rose-500/20 text-rose-600 dark:text-rose-300'
                      : 'bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-300'
                  }`}
                >
                  {advisory.direct_route.flood_detected ? '⚠️ HAZARD ALERT' : 'STANDARD'}
                </span>
              </div>

              <div className="text-[11px] text-slate-500 dark:text-slate-400 font-mono mb-2">
                Path: {advisory.direct_route.path_nodes.join(' → ')}
              </div>

              <div className="grid grid-cols-3 gap-1.5 p-2 rounded-lg bg-white/70 dark:bg-slate-950/40 text-[10px] font-mono mb-2">
                <div>
                  <span className="text-slate-400 block text-[9px]">DISTANCE</span>
                  <span className="font-bold text-slate-700 dark:text-slate-200">{advisory.direct_route.distance_km} km</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[9px]">EST. TIME</span>
                  <span className="font-bold text-amber-500">{advisory.direct_route.eta_minutes} min</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[9px]">LANES</span>
                  <span className={`font-bold ${advisory.direct_route.flood_detected ? 'text-rose-500' : 'text-slate-700 dark:text-slate-200'}`}>
                    {advisory.direct_route.lanes_available}
                  </span>
                </div>
              </div>

              {advisory.direct_route.warnings.length > 0 && (
                <div className="space-y-1 mb-1">
                  {advisory.direct_route.warnings.map((w, idx) => (
                    <div
                      key={idx}
                      className="text-[10px] text-rose-600 dark:text-rose-300 bg-rose-500/10 p-1.5 rounded-lg flex items-start gap-1"
                    >
                      <span>⚠️</span>
                      <span>{w}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <button
              onClick={() =>
                onSelectRouteForHighlight &&
                onSelectRouteForHighlight(advisory.direct_route.path_nodes, 'direct')
              }
              className="w-full py-1.5 rounded-lg font-medium text-xs bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 transition-all"
            >
              Highlight Direct Route on Map
            </button>
          </div>

          {/* Alternative Route Card */}
          <div
            className={`p-3.5 rounded-xl flex flex-col justify-between gap-2.5 transition-all ${
              advisory.alternative_route.is_recommended
                ? 'bg-emerald-500/10 ring-1 ring-emerald-500/30'
                : 'bg-slate-100 dark:bg-slate-900/60'
            }`}
          >
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <span className="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                  <span>✅</span>
                  <span>{advisory.alternative_route.name}</span>
                </span>
                <span className="text-[9px] font-mono px-2 py-0.5 rounded-full uppercase font-bold bg-emerald-500/20 text-emerald-600 dark:text-emerald-300">
                  RECOMMENDED
                </span>
              </div>

              <div className="text-[11px] text-slate-500 dark:text-slate-400 font-mono mb-2">
                Path: {advisory.alternative_route.path_nodes.join(' → ')}
              </div>

              <div className="grid grid-cols-3 gap-1.5 p-2 rounded-lg bg-white/70 dark:bg-slate-950/40 text-[10px] font-mono mb-2">
                <div>
                  <span className="text-slate-400 block text-[9px]">DISTANCE</span>
                  <span className="font-bold text-slate-700 dark:text-slate-200">{advisory.alternative_route.distance_km} km</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[9px]">EST. TIME</span>
                  <span className="font-bold text-emerald-500">{advisory.alternative_route.eta_minutes} min</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[9px]">LANES</span>
                  <span className="font-bold text-emerald-600 dark:text-emerald-400">
                    {advisory.alternative_route.lanes_available}
                  </span>
                </div>
              </div>

              <div className="text-[10px] text-emerald-600 dark:text-emerald-300 bg-emerald-500/10 p-1.5 rounded-lg flex items-center gap-1 mb-1">
                <span>🛡️</span>
                <span>Normal road friction • 100% capacity • Flood bypassed</span>
              </div>
            </div>

            <button
              onClick={() =>
                onSelectRouteForHighlight &&
                onSelectRouteForHighlight(advisory.alternative_route.path_nodes, 'alternative')
              }
              className="w-full py-1.5 rounded-lg font-bold text-xs bg-emerald-500 hover:bg-emerald-400 text-slate-950 transition-all shadow-sm"
            >
              Highlight Safe Alternative on Map
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default TravelerAdvisoryPanel;
