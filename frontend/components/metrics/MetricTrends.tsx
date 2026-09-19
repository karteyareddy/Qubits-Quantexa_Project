'use client';

import React, { useId } from 'react';
import { MetricHistoryPoint } from '../../hooks/useDashboard';

interface MetricTrendsProps {
  history: MetricHistoryPoint[];
}

interface TrendChartProps {
  label: string;
  eyebrow: string;
  values: number[];
  formattedValue: string;
  accent: string;
  note: string;
}

const CHART_WIDTH = 360;
const CHART_HEIGHT = 126;
const CHART_PADDING = 12;

function buildPoints(values: number[]): string {
  const safeValues = values.length > 1 ? values : [values[0] ?? 0, values[0] ?? 0];
  const maximum = Math.max(1, ...safeValues);
  return safeValues
    .map((value, index) => {
      const xPosition = CHART_PADDING + (index / (safeValues.length - 1)) * (CHART_WIDTH - CHART_PADDING * 2);
      const yPosition = CHART_HEIGHT - CHART_PADDING - (value / maximum) * (CHART_HEIGHT - CHART_PADDING * 2);
      return `${xPosition},${yPosition}`;
    })
    .join(' ');
}

const TrendChart: React.FC<TrendChartProps> = ({
  label,
  eyebrow,
  values,
  formattedValue,
  accent,
  note,
}) => {
  const gradientId = `trend-${useId().replaceAll(':', '')}`;
  const points = buildPoints(values);
  const areaPoints = `${CHART_PADDING},${CHART_HEIGHT - CHART_PADDING} ${points} ${CHART_WIDTH - CHART_PADDING},${CHART_HEIGHT - CHART_PADDING}`;
  const previous = values.at(-2) ?? values.at(-1) ?? 0;
  const current = values.at(-1) ?? 0;
  const direction = current > previous ? '↑' : current < previous ? '↓' : '→';

  return (
    <article className="trend-card rounded-2xl p-4 transition-all">
      <div className="trend-card__header flex items-start justify-between gap-2">
        <div>
          <span className="trend-card__eyebrow text-slate-400 text-[10px] font-bold tracking-widest uppercase block">
            {eyebrow}
          </span>
          <h4 className="text-slate-200 font-bold text-xs mt-0.5">{label}</h4>
        </div>
        <div className="trend-card__value text-right font-mono" style={{ color: accent }}>
          <span className="text-sm font-bold block">{formattedValue}</span>
          <small className="text-[10px] text-slate-400 uppercase font-semibold">{direction} live</small>
        </div>
      </div>

      <svg className="trend-chart w-full h-[126px] mt-2 overflow-visible" viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`} role="img" aria-label={`${label} trend`}>
        <defs>
          <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={accent} stopOpacity="0.25" />
            <stop offset="100%" stopColor={accent} stopOpacity="0" />
          </linearGradient>
        </defs>
        {[28, 61, 94].map((yPosition) => (
          <line
            key={yPosition}
            x1="12"
            x2="348"
            y1={yPosition}
            y2={yPosition}
            className="stroke-slate-800/40 stroke-[1] stroke-dasharray-[2,5]"
          />
        ))}
        <polygon points={areaPoints} fill={`url(#${gradientId})`} />
        <polyline points={points} fill="none" stroke={accent} strokeWidth="2.5" strokeLinejoin="round" strokeLinecap="round" />
        <circle
          cx={points.split(' ').at(-1)?.split(',')[0]}
          cy={points.split(' ').at(-1)?.split(',')[1]}
          r="4"
          fill={accent}
          className="trend-current-point drop-shadow-md"
        />
      </svg>
      <div className="trend-card__footer flex items-center justify-between text-[11px] text-slate-400 mt-2.5 pt-1.5">
        <span>{note}</span>
        <span className="font-mono">{historyWindow(values.length)}</span>
      </div>
    </article>
  );
};

function historyWindow(pointCount: number): string {
  return pointCount > 1 ? `${pointCount} samples` : 'calibrating';
}

export const MetricTrends: React.FC<MetricTrendsProps> = ({ history }) => {
  const latest = history.at(-1);

  return (
    <section className="analytics-panel rounded-2xl p-5 transition-all" id="analytics">
      <div className="panel-title-row flex items-center justify-between gap-4 mb-3.5">
        <div>
          <span className="panel-kicker text-cyan-400 font-mono font-bold text-[10px] tracking-widest uppercase block mb-0.5">
            Performance Metrics
          </span>
          <h3 className="text-slate-100 font-extrabold text-base tracking-tight m-0">
            Live Operational Analytics
          </h3>
        </div>
        <span className="panel-live-badge bg-emerald-500/15 text-emerald-400 px-3.5 py-1 rounded-full text-xs font-bold flex items-center gap-2 shadow-sm">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>STREAMING</span>
        </span>
      </div>

      <div className="analytics-grid">
        <TrendChart
          eyebrow="Mobility"
          label="Average Wait"
          values={history.map((point) => point.waitingTime)}
          formattedValue={`${(latest?.waitingTime ?? 0).toFixed(1)}s`}
          accent="#38bdf8"
          note="Per-vehicle signal delay"
        />
        <TrendChart
          eyebrow="Network"
          label="Queue Pressure"
          values={history.map((point) => point.queueLength)}
          formattedValue={`${latest?.queueLength ?? 0} veh`}
          accent="#a855f7"
          note="Vehicles currently on network"
        />
        <TrendChart
          eyebrow="Flow"
          label="Throughput"
          values={history.map((point) => point.throughput)}
          formattedValue={`${Math.round(latest?.throughput ?? 0)} v/h`}
          accent="#34d399"
          note={`${((latest?.completionRate ?? 0) * 100).toFixed(0)}% trip completion`}
        />
        <TrendChart
          eyebrow="Environment"
          label="CO₂ Footprint"
          values={history.map((point) => point.co2Kg)}
          formattedValue={`${(latest?.co2Kg ?? 0).toFixed(2)} kg`}
          accent="#f43f5e"
          note={`${(latest?.fuelLiters ?? 0).toFixed(2)} L fuel estimated`}
        />
      </div>
    </section>
  );
};
