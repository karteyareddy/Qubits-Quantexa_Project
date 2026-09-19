'use client';

import React from 'react';
import { OptimizationResponse } from '../../lib/types';
import { formatEnergy, formatNumber } from '../../lib/formatters';
import LatticeLoader from '../ui/LatticeLoader';

interface QuantumPanelProps {
  latestOptimization: OptimizationResponse | null;
  isOptimizing: boolean;
  id?: string;
}

export const QuantumPanel: React.FC<QuantumPanelProps> = ({
  latestOptimization,
  isOptimizing,
  id = 'quantum',
}) => {
  return (
    <div id={id} className="quantum-panel rounded-2xl p-5 shadow-xl space-y-3 transition-all">
      <div className="flex justify-between items-center">
        <h3 className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center space-x-2">
          <span>⚛</span>
          <span>HYBRID QUANTUM OPTIMIZER</span>
        </h3>
        <LatticeLoader
          status={isOptimizing ? 'working' : 'done'}
          label="QAOA Solving..."
          doneLabel="Optimal Phase Found"
          pattern="orbit"
          grid={3}
          glow
          color="#00f5ff"
          doneColor="#00ff9d"
          cellSize={3.5}
          gap={1.5}
          fontSize={10}
          showTimer={false}
        />
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
        <div className="bg-slate-100 dark:bg-slate-900/60 p-3 rounded-xl flex flex-col justify-center gap-0.5">
          <span className="text-slate-500 dark:text-slate-400 text-[10px] font-semibold block uppercase">SOLVER</span>
          <span className="font-bold text-slate-800 dark:text-slate-200 truncate block text-xs">
            {latestOptimization?.solver_name || 'QAOA / Hybrid'}
          </span>
        </div>

        <div className="bg-slate-100 dark:bg-slate-900/60 p-3 rounded-xl flex flex-col justify-center gap-0.5">
          <span className="text-slate-500 dark:text-slate-400 text-[10px] font-semibold block uppercase">BACKEND</span>
          <span className="font-bold text-cyan-600 dark:text-cyan-300 truncate block text-xs">
            Qiskit Aer (AerSim)
          </span>
        </div>

        <div className="bg-slate-100 dark:bg-slate-900/60 p-3 rounded-xl flex flex-col justify-center gap-0.5">
          <span className="text-slate-500 dark:text-slate-400 text-[10px] font-semibold block uppercase">QUBO ENERGY</span>
          <span className="font-mono font-bold text-amber-500 dark:text-amber-400 text-sm block">
            {formatEnergy(latestOptimization?.qubo_energy)}
          </span>
        </div>

        <div className="bg-slate-100 dark:bg-slate-900/60 p-3 rounded-xl flex flex-col justify-center gap-0.5">
          <span className="text-slate-500 dark:text-slate-400 text-[10px] font-semibold block uppercase">FEASIBLE / TIME</span>
          <span className="font-bold text-slate-800 dark:text-slate-200 block text-xs">
            {latestOptimization ? (
              <>
                <span className={latestOptimization.is_feasible ? 'text-emerald-500 dark:text-emerald-400' : 'text-rose-500 dark:text-rose-400'}>
                  {latestOptimization.is_feasible ? 'YES' : 'NO'}
                </span>{' '}
                <span className="text-slate-500 dark:text-slate-400 font-normal">
                  ({formatNumber(latestOptimization.optimization_time_seconds * 1000, 0)}ms)
                </span>
              </>
            ) : (
              '--'
            )}
          </span>
        </div>
      </div>

      {latestOptimization?.fallback_used && (
        <div className="bg-amber-500/10 p-3 rounded-xl text-xs text-amber-400 flex items-center justify-between">
          <span className="font-medium">⚠️ Classical fallback executed; QAOA result within bound.</span>
          <span className="text-[10px] font-mono text-slate-400">
            {latestOptimization.fallback_reason || 'Classical Fallback'}
          </span>
        </div>
      )}
    </div>
  );
};
