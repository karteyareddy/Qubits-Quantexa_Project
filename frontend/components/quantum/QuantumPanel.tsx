'use client';

import React from 'react';
import { OptimizationResponse } from '../../lib/types';
import { formatEnergy, formatNumber } from '../../lib/formatters';

interface QuantumPanelProps {
  latestOptimization: OptimizationResponse | null;
  isOptimizing: boolean;
}

export const QuantumPanel: React.FC<QuantumPanelProps> = ({
  latestOptimization,
  isOptimizing,
}) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-md space-y-3">
      <div className="flex justify-between items-center">
        <h3 className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center space-x-2">
          <span>⚛</span>
          <span>HYBRID QUANTUM OPTIMIZER</span>
        </h3>
        {isOptimizing && (
          <span className="text-xs bg-cyan-950 text-cyan-300 border border-cyan-800 px-2 py-0.5 rounded font-mono animate-pulse">
            RUNNING QAOA...
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
        <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
          <span className="text-slate-400 text-[10px] block">SOLVER</span>
          <span className="font-semibold text-slate-200">
            {latestOptimization?.solver_name || 'QAOA / Hybrid'}
          </span>
        </div>

        <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
          <span className="text-slate-400 text-[10px] block">BACKEND</span>
          <span className="font-semibold text-cyan-300">Qiskit Aer (AerSimulator)</span>
        </div>

        <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
          <span className="text-slate-400 text-[10px] block">QUBO ENERGY</span>
          <span className="font-mono font-bold text-amber-300">
            {formatEnergy(latestOptimization?.qubo_energy)}
          </span>
        </div>

        <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
          <span className="text-slate-400 text-[10px] block">FEASIBLE / TIME</span>
          <span className="font-semibold text-slate-200">
            {latestOptimization ? (
              <>
                <span className={latestOptimization.is_feasible ? 'text-emerald-400' : 'text-rose-400'}>
                  {latestOptimization.is_feasible ? 'YES' : 'NO'}
                </span>{' '}
                ({formatNumber(latestOptimization.optimization_time_seconds * 1000, 0)}ms)
              </>
            ) : (
              '--'
            )}
          </span>
        </div>
      </div>

      {latestOptimization?.fallback_used && (
        <div className="bg-amber-950/40 border border-amber-800/60 p-2.5 rounded text-xs text-amber-300 flex items-center justify-between">
          <span>⚠️ Quantum circuit qubit limit exceeded; fallback classical solver executed.</span>
          <span className="text-[10px] font-mono text-slate-400">
            {latestOptimization.fallback_reason || 'Classical Fallback'}
          </span>
        </div>
      )}
    </div>
  );
};
