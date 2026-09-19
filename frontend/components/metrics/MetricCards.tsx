'use client';

import React from 'react';
import { SimulationMetricsResponse } from '../../lib/types';
import { formatNumber, formatTime } from '../../lib/formatters';

interface MetricCardsProps {
  metrics: SimulationMetricsResponse | null;
}

export const MetricCards: React.FC<MetricCardsProps> = ({ metrics }) => {
  const completion = Math.min(100, Math.max(0, (metrics?.completion_rate ?? 0) * 100));
  const cards = [
    {
      label: 'Average Wait',
      value: formatTime(metrics?.average_waiting_time_seconds ?? 0),
      detail: 'Signal delay / vehicle',
      icon: '◷',
      tone: 'cyan',
    },
    {
      label: 'Network Flow',
      value: `${formatNumber(metrics?.throughput_vph ?? 0, 0)} v/h`,
      detail: 'Completed vehicle rate',
      icon: '⇥',
      tone: 'green',
    },
    {
      label: 'Fleet State',
      value: `${metrics?.active_vehicles ?? 0} / ${metrics?.total_vehicles ?? 0}`,
      detail: `${formatNumber(completion, 1)}% complete`,
      icon: '⬡',
      tone: 'indigo',
      progress: completion,
    },
    {
      label: 'Fuel Model',
      value: `${formatNumber(metrics?.total_fuel_consumed_liters ?? 0, 2)} L`,
      detail: 'Estimated consumption',
      icon: '◈',
      tone: 'amber',
    },
    {
      label: 'CO₂ Footprint',
      value: `${formatNumber(metrics?.total_co2_emitted_kg ?? 0, 2)} kg`,
      detail: 'Estimated emissions',
      icon: '◌',
      tone: 'rose',
    },
    {
      label: 'Priority Link',
      value: metrics?.emergency_corridor_active ? 'ACTIVE' : 'STANDBY',
      detail: `Emergency wait ${formatTime(metrics?.emergency_waiting_time_seconds ?? 0)}`,
      icon: '✚',
      tone: metrics?.emergency_corridor_active ? 'amber' : 'slate',
      active: metrics?.emergency_corridor_active,
    },
  ];

  return (
    <section className="metric-grid" aria-label="Live simulation metrics">
      {cards.map((card) => (
        <article key={card.label} className={`metric-card metric-card--${card.tone}`}>
          <div className="metric-card__topline">
            <span>{card.label}</span>
            <i className={card.active ? 'metric-card__icon is-pulsing' : 'metric-card__icon'}>{card.icon}</i>
          </div>
          <strong>{card.value}</strong>
          <small>{card.detail}</small>
          {card.progress !== undefined && (
            <div className="metric-progress"><span style={{ width: `${card.progress}%` }} /></div>
          )}
        </article>
      ))}
    </section>
  );
};
