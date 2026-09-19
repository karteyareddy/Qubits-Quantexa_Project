export function formatTime(seconds: number): string {
  if (isNaN(seconds) || seconds == null) return '0.0s';
  return `${seconds.toFixed(1)}s`;
}

export function formatEnergy(energy: number | null | undefined): string {
  if (energy == null || isNaN(energy)) return 'N/A';
  return energy.toFixed(3);
}

export function formatNumber(val: number | null | undefined, decimals: number = 1): string {
  if (val == null || isNaN(val)) return '0';
  return val.toFixed(decimals);
}

export function formatPhaseName(phase: string | null | undefined): string {
  if (!phase) return 'UNKNOWN';
  if (phase === 'EW_GREEN') return 'EW GREEN (Phase 0)';
  if (phase === 'NS_GREEN') return 'NS GREEN (Phase 1)';
  return phase;
}
