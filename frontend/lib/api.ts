import {
  EmergencyCorridorResponse,
  EventInjectPayload,
  EventRecordResponse,
  NetworkSchema,
  OptimizationRequest,
  OptimizationResponse,
  ScenarioMetadataSchema,
  SimulationCreateRequest,
  SimulationMetricsResponse,
  SimulationSessionResponse,
  SimulationStateSnapshot,
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function fetchJSON<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...(options?.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    let errorMsg = `HTTP Error ${response.status} ${response.statusText}`;
    try {
      const errData = await response.json();
      if (errData.error?.message) {
        errorMsg = errData.error.message;
      } else if (errData.detail) {
        errorMsg = typeof errData.detail === 'string' ? errData.detail : JSON.stringify(errData.detail);
      }
    } catch {
      // Ignore JSON parse errors for fallback errorMsg
    }
    throw new Error(errorMsg);
  }

  return response.json() as Promise<T>;
}

export const api = {
  getNetwork: (): Promise<NetworkSchema> => {
    return fetchJSON<NetworkSchema>('/api/v1/network');
  },

  getScenarios: (): Promise<ScenarioMetadataSchema[]> => {
    return fetchJSON<ScenarioMetadataSchema[]>('/api/v1/scenarios');
  },

  createSimulation: (req?: SimulationCreateRequest): Promise<SimulationSessionResponse> => {
    return fetchJSON<SimulationSessionResponse>('/api/v1/simulations', {
      method: 'POST',
      body: JSON.stringify(req || {}),
    });
  },

  getSimulation: (simulationId: string): Promise<SimulationStateSnapshot> => {
    return fetchJSON<SimulationStateSnapshot>(`/api/v1/simulations/${simulationId}`);
  },

  startSimulation: (simulationId: string): Promise<SimulationSessionResponse> => {
    return fetchJSON<SimulationSessionResponse>(`/api/v1/simulations/${simulationId}/start`, {
      method: 'POST',
    });
  },

  pauseSimulation: (simulationId: string): Promise<SimulationSessionResponse> => {
    return fetchJSON<SimulationSessionResponse>(`/api/v1/simulations/${simulationId}/pause`, {
      method: 'POST',
    });
  },

  stepSimulation: (simulationId: string, stepSeconds: number = 1.0): Promise<SimulationStateSnapshot> => {
    return fetchJSON<SimulationStateSnapshot>(`/api/v1/simulations/${simulationId}/step`, {
      method: 'POST',
      body: JSON.stringify({ step_seconds: stepSeconds }),
    });
  },

  stopSimulation: (simulationId: string): Promise<SimulationSessionResponse> => {
    return fetchJSON<SimulationSessionResponse>(`/api/v1/simulations/${simulationId}/stop`, {
      method: 'POST',
    });
  },

  optimizeSimulation: (simulationId: string, req?: OptimizationRequest): Promise<OptimizationResponse> => {
    return fetchJSON<OptimizationResponse>(`/api/v1/simulations/${simulationId}/optimize`, {
      method: 'POST',
      body: JSON.stringify(req || { solver: 'hybrid', apply_immediately: true }),
    });
  },

  getMetrics: (simulationId: string): Promise<SimulationMetricsResponse> => {
    return fetchJSON<SimulationMetricsResponse>(`/api/v1/simulations/${simulationId}/metrics`);
  },

  getEvents: (simulationId: string): Promise<EventRecordResponse[]> => {
    return fetchJSON<EventRecordResponse[]>(`/api/v1/simulations/${simulationId}/events`);
  },

  injectEvent: (simulationId: string, payload: EventInjectPayload): Promise<EventRecordResponse> => {
    return fetchJSON<EventRecordResponse>(`/api/v1/simulations/${simulationId}/events`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  getEmergencyCorridors: (simulationId: string): Promise<EmergencyCorridorResponse[]> => {
    return fetchJSON<EmergencyCorridorResponse[]>(`/api/v1/simulations/${simulationId}/emergency`);
  },

  activateEmergencyCorridor: (simulationId: string, vehicleId: string): Promise<EmergencyCorridorResponse> => {
    return fetchJSON<EmergencyCorridorResponse>(
      `/api/v1/simulations/${simulationId}/emergency/${vehicleId}/activate`,
      { method: 'POST' }
    );
  },
};
