'use client';

import React, { useState, useEffect } from 'react';

export interface WeatherZoneState {
  zone_id: string;
  name: string;
  condition: string;
  temperature_c: number;
  rain_intensity_mmh: number;
  visibility_km: number;
  water_level_cm: number;
  capacity_factor: number;
  speed_factor: number;
  lane_availability: number;
  risk_factor: number;
}

interface WeatherControlPanelProps {
  id?: string;
  onWeatherChanged?: () => void;
}

export const WeatherControlPanel: React.FC<WeatherControlPanelProps> = ({ id = 'weather', onWeatherChanged }) => {
  const [zones, setZones] = useState<Record<string, WeatherZoneState>>({
    'zone-1': {
      zone_id: 'zone-1',
      name: 'Zone 1: Northwest Hub',
      condition: 'clear',
      temperature_c: 24,
      rain_intensity_mmh: 0,
      visibility_km: 10,
      water_level_cm: 0,
      capacity_factor: 1.0,
      speed_factor: 1.0,
      lane_availability: 1.0,
      risk_factor: 0.0,
    },
    'zone-2': {
      zone_id: 'zone-2',
      name: 'Zone 2: Central Corridor',
      condition: 'heavy_rain',
      temperature_c: 19,
      rain_intensity_mmh: 45,
      visibility_km: 3.5,
      water_level_cm: 6,
      capacity_factor: 0.7,
      speed_factor: 0.75,
      lane_availability: 1.0,
      risk_factor: 0.5,
    },
    'zone-3': {
      zone_id: 'zone-3',
      name: 'Zone 3: East Tech Hub',
      condition: 'fog',
      temperature_c: 16,
      rain_intensity_mmh: 0,
      visibility_km: 0.8,
      water_level_cm: 0,
      capacity_factor: 0.65,
      speed_factor: 0.5,
      lane_availability: 1.0,
      risk_factor: 0.7,
    },
    'zone-4': {
      zone_id: 'zone-4',
      name: 'Zone 4: South Civic',
      condition: 'clear',
      temperature_c: 23,
      rain_intensity_mmh: 0,
      visibility_km: 10,
      water_level_cm: 0,
      capacity_factor: 1.0,
      speed_factor: 1.0,
      lane_availability: 1.0,
      risk_factor: 0.0,
    },
  });

  const [isUpdating, setIsUpdating] = useState<string | null>(null);

  const fetchZones = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/weather/zones');
      if (res.ok) {
        const data = await res.json();
        if (data.summary) {
          setZones((prev) => ({
            ...prev,
            ...Object.fromEntries(
              Object.entries(data.summary).map(([zId, z]: [string, any]) => [
                zId,
                { ...z, zone_id: zId },
              ])
            ),
          }));
        }
      }
    } catch {
      // Offline fallback
    }
  };

  useEffect(() => {
    fetchZones();
    const interval = setInterval(fetchZones, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleUpdateCondition = async (zoneId: string, condition: string) => {
    setIsUpdating(zoneId);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/weather/zones/${zoneId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          condition,
          water_level_cm: condition === 'flooding' ? 15.0 : condition === 'heavy_rain' ? 6.0 : 0.0,
          rain_intensity_mmh: condition === 'heavy_rain' ? 45.0 : condition === 'flooding' ? 70.0 : 0.0,
          visibility_km: condition === 'fog' ? 0.8 : condition === 'mist' ? 2.0 : condition === 'flooding' ? 2.0 : 10.0,
        }),
      });
      if (res.ok) {
        await fetchZones();
        if (onWeatherChanged) onWeatherChanged();
      }
    } catch (err) {
      console.error('Failed to update weather zone:', err);
    } finally {
      setIsUpdating(null);
    }
  };

  const getConditionIcon = (cond: string) => {
    switch (cond) {
      case 'clear':
        return '☀️';
      case 'light_rain':
        return '🌦️';
      case 'heavy_rain':
        return '🌧️';
      case 'flooding':
        return '🌊';
      case 'fog':
      case 'mist':
        return '🌫️';
      default:
        return '☁️';
    }
  };

  return (
    <div id={id} className="weather-panel rounded-2xl p-5 shadow-xl space-y-3.5 transition-all">
      <div className="flex justify-between items-center">
        <h3 className="text-xs font-bold text-cyan-500 dark:text-cyan-400 uppercase tracking-wider flex items-center space-x-2">
          <span>🌦️</span>
          <span>WEATHER INTELLIGENCE & MULTI-ZONE ENGINE</span>
        </h3>
        <span className="text-[10px] font-mono font-semibold px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-600 dark:text-cyan-400">
          4 LIVE ZONES
        </span>
      </div>

      <p className="text-xs text-slate-500 dark:text-slate-400">
        Zone-specific meteorological conditions dynamically scale road capacities, cruising speeds, and QUBO penalties.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
        {Object.entries(zones).map(([zoneId, zone]) => {
          const isFlooded = zone.condition === 'flooding';
          const isFog = zone.condition === 'fog' || zone.condition === 'mist';
          const isRain = zone.condition === 'heavy_rain';

          return (
            <div
              key={zoneId}
              className={`p-3.5 rounded-xl flex flex-col justify-between gap-2.5 transition-all ${
                isFlooded
                  ? 'bg-blue-500/10 ring-1 ring-blue-500/30'
                  : isFog
                  ? 'bg-purple-500/10 ring-1 ring-purple-500/30'
                  : isRain
                  ? 'bg-sky-500/10 ring-1 ring-sky-500/30'
                  : 'bg-slate-100 dark:bg-slate-900/60'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5 text-xs truncate">
                  <span>{getConditionIcon(zone.condition)}</span>
                  <span className="truncate">{zone.name.split('-')[0].trim()}</span>
                </span>
                <span
                  className={`text-[9px] font-mono px-2 py-0.5 rounded-full uppercase font-bold ${
                    isFlooded
                      ? 'bg-blue-500/20 text-blue-600 dark:text-blue-300'
                      : isFog
                      ? 'bg-purple-500/20 text-purple-600 dark:text-purple-300'
                      : isRain
                      ? 'bg-sky-500/20 text-sky-600 dark:text-sky-300'
                      : 'bg-emerald-500/20 text-emerald-600 dark:text-emerald-300'
                  }`}
                >
                  {zone.condition}
                </span>
              </div>

              {/* Physical Impact Stats */}
              <div className="grid grid-cols-2 gap-1.5 p-2 rounded-lg bg-white/70 dark:bg-slate-950/40 text-[10px] font-mono">
                <div>
                  <span className="text-slate-400 block text-[9px]">CAPACITY</span>
                  <span
                    className={`font-bold ${
                      zone.capacity_factor < 0.6 ? 'text-rose-500' : 'text-slate-700 dark:text-slate-200'
                    }`}
                  >
                    {Math.round(zone.capacity_factor * 100)}%
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[9px]">SPEED</span>
                  <span
                    className={`font-bold ${
                      zone.speed_factor < 0.6 ? 'text-amber-500' : 'text-slate-700 dark:text-slate-200'
                    }`}
                  >
                    {Math.round(zone.speed_factor * 100)}%
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[9px]">WATER</span>
                  <span className={zone.water_level_cm > 5 ? 'text-blue-500 font-bold' : 'text-slate-600 dark:text-slate-400'}>
                    {zone.water_level_cm || 0} cm
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[9px]">VISIBILITY</span>
                  <span className={zone.visibility_km < 1 ? 'text-purple-500 font-bold' : 'text-slate-600 dark:text-slate-400'}>
                    {zone.visibility_km || 10} km
                  </span>
                </div>
              </div>

              {isFlooded && (
                <div className="text-[10px] text-blue-600 dark:text-blue-300 font-semibold flex items-center gap-1 bg-blue-500/15 px-2 py-1 rounded-lg">
                  <span>🌊</span>
                  <span>1 Lane Blocked • Water Flow</span>
                </div>
              )}

              {/* Quick Switch Buttons */}
              <div className="flex items-center justify-between gap-1 pt-1">
                <span className="text-[9px] text-slate-400 uppercase font-mono">SET:</span>
                <div className="flex items-center gap-1">
                  {[
                    { key: 'clear', label: '☀️', name: 'Clear' },
                    { key: 'heavy_rain', label: '🌧️', name: 'Rain' },
                    { key: 'flooding', label: '🌊', name: 'Flood' },
                    { key: 'fog', label: '🌫️', name: 'Fog' },
                  ].map((btn) => (
                    <button
                      key={btn.key}
                      disabled={isUpdating === zoneId}
                      onClick={() => handleUpdateCondition(zoneId, btn.key)}
                      title={`Set ${zone.name} to ${btn.name}`}
                      className={`text-xs px-2 py-0.5 rounded-lg transition-all ${
                        zone.condition === btn.key
                          ? 'bg-cyan-500 text-slate-950 font-bold shadow-sm'
                          : 'bg-slate-200 dark:bg-slate-800/80 hover:bg-slate-300 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300'
                      }`}
                    >
                      {btn.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default WeatherControlPanel;
