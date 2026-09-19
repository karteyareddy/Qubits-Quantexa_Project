'use client';

import React from 'react';
import { EventRecordResponse } from '../../lib/types';
import { formatTime } from '../../lib/formatters';

interface EventTimelineProps {
  events: EventRecordResponse[];
}

export const EventTimeline: React.FC<EventTimelineProps> = ({ events }) => {
  if (events.length === 0) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-md text-xs">
        <h3 className="font-bold text-slate-300 uppercase tracking-wider mb-2">
          Dynamic Events Log
        </h3>
        <p className="text-slate-500 italic">No dynamic events injected or scheduled yet.</p>
      </div>
    );
  }

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'bg-amber-950 text-amber-300 border-amber-800';
      case 'expired':
        return 'bg-slate-950 text-slate-500 border-slate-800';
      case 'scheduled':
        return 'bg-blue-950 text-blue-300 border-blue-800';
      case 'failed':
        return 'bg-rose-950 text-rose-300 border-rose-800';
      default:
        return 'bg-slate-950 text-slate-400 border-slate-800';
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-md space-y-3">
      <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
        Dynamic Events Log ({events.length})
      </h3>

      <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
        {events.map((ev) => (
          <div
            key={ev.event_id}
            className="bg-slate-950 p-2.5 rounded-lg border border-slate-800 flex items-center justify-between text-xs"
          >
            <div className="flex items-center space-x-2">
              <span className="font-mono text-cyan-400">{formatTime(ev.starts_at_seconds)}</span>
              <span className="font-semibold text-slate-200 uppercase">{ev.event_type}</span>
              <span className="text-slate-400 text-[10px]">({ev.target})</span>
            </div>

            <span
              className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${getStatusBadge(
                ev.status
              )}`}
            >
              {ev.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
