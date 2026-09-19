'use client';

import React, { useState } from 'react';
import { EventInjectPayload } from '../../lib/types';

interface EventInjectionModalProps {
  simulationTime: number;
  onInject: (payload: EventInjectPayload) => void;
  onClose: () => void;
  isInjecting: boolean;
}

export const EventInjectionModal: React.FC<EventInjectionModalProps> = ({
  simulationTime,
  onInject,
  onClose,
  isInjecting,
}) => {
  const [eventType, setEventType] = useState<'congestion_spike' | 'accident' | 'road_closure' | 'emergency_arrival'>(
    'congestion_spike'
  );

  const [edgeId, setEdgeId] = useState<string>('I1-I2');
  const [multiplier, setMultiplier] = useState<number>(2.5);
  const [duration, setDuration] = useState<number>(30.0);
  const [capacityReduction, setCapacityReduction] = useState<number>(0.5);

  const [vehicleId, setVehicleId] = useState<string>('emergency-event-001');
  const [origin, setOrigin] = useState<string>('I1');
  const [destination, setDestination] = useState<string>('I6');
  const [priorityWeight, setPriorityWeight] = useState<number>(20);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    let payload: EventInjectPayload;

    if (eventType === 'congestion_spike') {
      payload = {
        type: 'congestion_spike',
        timestamp: simulationTime + 1.0,
        edge_id: edgeId,
        multiplier,
        duration,
      };
    } else if (eventType === 'accident') {
      payload = {
        type: 'accident',
        timestamp: simulationTime + 1.0,
        edge_id: edgeId,
        capacity_reduction: capacityReduction,
        duration,
      };
    } else if (eventType === 'road_closure') {
      payload = {
        type: 'road_closure',
        timestamp: simulationTime + 1.0,
        target: edgeId,
        duration,
      };
    } else {
      payload = {
        type: 'emergency_arrival',
        timestamp: simulationTime + 1.0,
        vehicle_id: vehicleId,
        origin,
        destination,
        priority_weight: priorityWeight,
      };
    }

    onInject(payload);
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 text-slate-100 rounded-xl shadow-2xl max-w-lg w-full p-6 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-slate-200 text-lg font-bold"
        >
          ✕
        </button>

        <h3 className="text-base font-bold text-amber-400 uppercase tracking-wider mb-4 flex items-center space-x-2">
          <span>⚡</span>
          <span>Inject Dynamic Traffic Event</span>
        </h3>

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          {/* Event Type Switcher */}
          <div>
            <label className="text-slate-400 font-semibold block mb-1">Event Type</label>
            <select
              value={eventType}
              onChange={(e) =>
                setEventType(
                  e.target.value as 'congestion_spike' | 'accident' | 'road_closure' | 'emergency_arrival'
                )
              }
              className="w-full bg-slate-950 text-slate-100 border border-slate-700 rounded-lg px-3 py-2 font-medium focus:outline-none focus:border-amber-500"
            >
              <option value="congestion_spike">Congestion Spike</option>
              <option value="accident">Traffic Accident</option>
              <option value="road_closure">Road Closure</option>
              <option value="emergency_arrival">Emergency Vehicle Arrival</option>
            </select>
          </div>

          {/* Conditional Input Fields */}
          {eventType !== 'emergency_arrival' ? (
            <>
              <div>
                <label className="text-slate-400 font-semibold block mb-1">Target Edge</label>
                <select
                  value={edgeId}
                  onChange={(e) => setEdgeId(e.target.value)}
                  className="w-full bg-slate-950 text-slate-100 border border-slate-700 rounded-lg px-3 py-2 font-mono"
                >
                  <option value="I1-I2">I1-I2</option>
                  <option value="I2-I3">I2-I3</option>
                  <option value="I4-I5">I4-I5</option>
                  <option value="I5-I6">I5-I6</option>
                  <option value="I1-I4">I1-I4</option>
                  <option value="I2-I5">I2-I5</option>
                  <option value="I3-I6">I3-I6</option>
                </select>
              </div>

              {eventType === 'congestion_spike' && (
                <div>
                  <label className="text-slate-400 font-semibold block mb-1">
                    Travel Time Multiplier ({multiplier}x)
                  </label>
                  <input
                    type="range"
                    min="1.5"
                    max="5.0"
                    step="0.5"
                    value={multiplier}
                    onChange={(e) => setMultiplier(parseFloat(e.target.value))}
                    className="w-full"
                  />
                </div>
              )}

              {eventType === 'accident' && (
                <div>
                  <label className="text-slate-400 font-semibold block mb-1">
                    Capacity Reduction ({Math.round(capacityReduction * 100)}%)
                  </label>
                  <input
                    type="range"
                    min="0.1"
                    max="0.9"
                    step="0.1"
                    value={capacityReduction}
                    onChange={(e) => setCapacityReduction(parseFloat(e.target.value))}
                    className="w-full"
                  />
                </div>
              )}

              <div>
                <label className="text-slate-400 font-semibold block mb-1">Duration (seconds)</label>
                <input
                  type="number"
                  min="5"
                  max="300"
                  value={duration}
                  onChange={(e) => setDuration(parseFloat(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 font-mono"
                />
              </div>
            </>
          ) : (
            <>
              <div>
                <label className="text-slate-400 font-semibold block mb-1">Vehicle ID</label>
                <input
                  type="text"
                  value={vehicleId}
                  onChange={(e) => setVehicleId(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 font-mono"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-400 font-semibold block mb-1">Origin Node</label>
                  <input
                    type="text"
                    value={origin}
                    onChange={(e) => setOrigin(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 font-mono"
                  />
                </div>
                <div>
                  <label className="text-slate-400 font-semibold block mb-1">Destination Node</label>
                  <input
                    type="text"
                    value={destination}
                    onChange={(e) => setDestination(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="text-slate-400 font-semibold block mb-1">Priority Weight</label>
                <input
                  type="number"
                  min="1"
                  max="100"
                  value={priorityWeight}
                  onChange={(e) => setPriorityWeight(parseInt(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 font-mono"
                />
              </div>
            </>
          )}

          <div className="mt-6 flex justify-end space-x-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold px-4 py-2 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isInjecting}
              className="bg-amber-600 hover:bg-amber-500 text-white font-bold px-4 py-2 rounded-lg shadow-md transition-colors disabled:opacity-50"
            >
              {isInjecting ? 'Injecting...' : 'Submit Event'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
