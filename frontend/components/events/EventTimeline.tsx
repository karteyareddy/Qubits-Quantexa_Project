'use client';

import React from 'react';
import { EventRecordResponse } from '../../lib/types';
import { formatTime } from '../../lib/formatters';

interface EventTimelineProps {
  events: EventRecordResponse[];
  id?: string;
}

export const EventTimeline: React.FC<EventTimelineProps> = ({ events, id = 'events' }) => {
  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'bg-amber-500/20 text-amber-500 dark:text-amber-300';
      case 'expired':
        return 'bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400';
      case 'scheduled':
        return 'bg-blue-500/20 text-blue-600 dark:text-blue-300';
      case 'failed':
        return 'bg-rose-500/20 text-rose-600 dark:text-rose-300';
      default:
        return 'bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300';
    }
  };

  return (
    <div id={id} className="timeline-panel rounded-2xl p-5 shadow-xl transition-all h-full flex flex-col justify-between">
      {/* Header aligned exactly with ClassicalComparison */}
      <div className="flex items-center justify-between h-6 mb-3">
        <h3 className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
          Dynamic Events Log {events.length > 0 ? `(${events.length})` : ''}
        </h3>
        <span className="text-[10px] font-mono text-cyan-600 dark:text-cyan-400 font-semibold">
          {events.length > 0 ? 'LIVE LOG' : 'STANDBY'}
        </span>
      </div>

      {events.length === 0 ? (
        /* Clean empty state that keeps header at top and fills body symmetrically */
        <div className="flex-1 flex flex-col items-center justify-center py-4 text-center">
          <span className="text-2xl mb-1.5 opacity-60">⚡</span>
          <p className="text-slate-500 dark:text-slate-400 text-xs italic">
            No dynamic events injected or scheduled yet.
          </p>
          <span className="text-[11px] text-slate-400 dark:text-slate-500 mt-1">
            Click &apos;⚡ Inject Event&apos; above to simulate road incidents or lane closures.
          </span>
        </div>
      ) : (
        /* Scrollable events list */
        <div className="space-y-2 max-h-48 overflow-y-auto pr-1 flex-1">
          {events.map((ev) => (
            <div
              key={ev.event_id}
              className="bg-slate-100 dark:bg-slate-900/60 p-3 rounded-xl flex items-center justify-between text-xs transition-colors"
            >
              <div className="flex items-center space-x-2">
                <span className="font-mono font-bold text-cyan-600 dark:text-cyan-400">
                  {formatTime(ev.starts_at_seconds)}
                </span>
                <span className="font-semibold text-slate-800 dark:text-slate-200 uppercase">
                  {ev.event_type}
                </span>
                <span className="text-slate-500 dark:text-slate-400 text-[10px]">
                  ({ev.target})
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`text-[10px] px-2.5 py-0.5 rounded-full font-bold uppercase ${getStatusBadge(ev.status)}`}>
                  {ev.status}
                </span>
                <span className="text-slate-500 dark:text-slate-400 text-[10px] font-mono">
                  +{ev.duration_seconds}s
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Footer Meta Row aligned with ClassicalComparison */}
      <div className="text-[11px] text-slate-500 dark:text-slate-400 flex items-center justify-between pt-2 border-t border-slate-200/50 dark:border-slate-800/50 mt-auto">
        <span>Incident Dispatch Monitor</span>
        <span className="font-mono text-slate-500 dark:text-slate-400">
          {events.length} Active / Scheduled
        </span>
      </div>
    </div>
  );
};
