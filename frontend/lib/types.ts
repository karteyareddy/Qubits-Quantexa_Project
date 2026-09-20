/**
 * Stage 14 & 15 Frontend API & State TypeScript Models
 * Strictly mirrors backend FastAPI schemas in backend/app/api/schemas/
 */

export interface IntersectionSchema {
  intersection_id: string;
  name: string;
  is_signalized: boolean;
  position: [number, number] | null;
}

export interface EdgeSchema {
  edge_id: string;
  source_intersection: string;
  target_intersection: string;
  free_flow_travel_time_seconds: number;
  capacity: number;
  length_meters: number;
}

export interface NetworkSchema {
  intersections: IntersectionSchema[];
  edges: EdgeSchema[];
  signalized_intersections: string[];
}

export interface ScenarioMetadataSchema {
  scenario_id: string;
  name: string;
  description: string;
  duration_seconds: number;
  vehicle_count: number;
  emergency_vehicle_count: number;
}

export interface SimulationCreateRequest {
  scenario_id?: string;
  duration_seconds?: number | null;
  control_interval_seconds?: number;
  seed?: number;
  adaptive_enabled?: boolean;
  events_enabled?: boolean;
  emergency_corridor_enabled?: boolean;
}

export interface VehicleStateSchema {
  vehicle_id: string;
  origin: string;
  destination: string;
  current_edge_id: string | null;
  route: string[];
  route_index: number;
  arrival_time_seconds: number;
  distance_on_current_edge_meters: number;
  accumulated_waiting_time_seconds: number;
  speed_mps: number;
  is_emergency: boolean;
  emergency_subtype?: string | null;
  priority_weight: number;
  has_arrived: boolean;
  departure_time_seconds?: number | null;
}

export interface SignalStateSchema {
  intersection_id: string;
  current_phase: string;
  time_in_phase_seconds: number;
  active_green_approaches: string[];
}

export interface EdgeStateSchema {
  edge_id: string;
  vehicle_ids: string[];
  vehicle_count: number;
  capacity: number;
  effective_capacity: number;
  travel_time_multiplier: number;
  is_closed: boolean;
}

export interface ActiveEventSnapshot {
  event_id: string;
  event_type: string;
  timestamp: number;
  duration: number;
  status: string;
  target: string;
}

export interface SimulationSessionResponse {
  simulation_id: string;
  status: string;
  scenario_id: string;
  simulation_time_seconds: number;
  created_at: number;
}

export interface SimulationStateSnapshot {
  simulation_id: string;
  status: string;
  simulation_time_seconds: number;
  vehicles: VehicleStateSchema[];
  signals: SignalStateSchema[];
  edges: EdgeStateSchema[];
  active_events: ActiveEventSnapshot[];
  emergency_corridors: EmergencyCorridorResponse[];
  metrics: SimulationMetricsResponse;
  latest_optimization: OptimizationResponse | null;
  weather?: Record<string, any>;
}

export interface OptimizationRequest {
  solver?: string;
  apply_immediately?: boolean;
}

export interface SignalScheduleItemSchema {
  intersection_id: string;
  selected_phase: string;
  phase_duration_seconds: number;
}

export interface OptimizationResponse {
  simulation_id: string;
  timestamp: number;
  solver_name: string;
  qubo_energy: number | null;
  is_feasible: boolean;
  selected_schedule: Record<string, string> | null;
  optimization_time_seconds: number;
  fallback_used: boolean;
  fallback_reason?: string | null;
  applied_to_simulation: boolean;
  schedule_details: SignalScheduleItemSchema[];
  raw_metrics: Record<string, unknown>;
}

export interface GreenWindowResponse {
  intersection_id: string;
  arrival_time_seconds: number;
  window_start_seconds: number;
  window_end_seconds: number;
  incoming_approach: string;
  outgoing_approach: string;
  required_phase: string;
}

export interface EmergencyCorridorResponse {
  corridor_id: string;
  vehicle_id: string;
  route: string[];
  intersections: string[];
  status: string;
  created_at_seconds: number;
  activated_at_seconds?: number | null;
  released_at_seconds?: number | null;
  green_windows: GreenWindowResponse[];
  failure_reason?: string | null;
}

export interface SimulationMetricsResponse {
  simulation_id: string;
  simulation_time_seconds: number;
  total_vehicles: number;
  active_vehicles: number;
  arrived_vehicles: number;
  completion_rate: number;
  throughput_vph: number;
  average_travel_time_seconds: number;
  average_waiting_time_seconds: number;
  total_fuel_consumed_liters: number;
  total_co2_emitted_kg: number;
  emergency_waiting_time_seconds: number;
  emergency_travel_time_seconds: number;
  emergency_corridor_active: boolean;
  event_impact_summary: Record<string, unknown>;
  optimization_summary: Record<string, unknown>;
}

export interface EventRecordResponse {
  event_id: string;
  event_type: string;
  starts_at_seconds: number;
  duration_seconds?: number | null;
  status: string;
  target: string;
  applied_at_seconds?: number | null;
  expired_at_seconds?: number | null;
  failure_reason?: string | null;
}

export interface CongestionSpikeEventPayload {
  type: 'congestion_spike';
  timestamp: number;
  edge_id: string;
  multiplier?: number;
  duration?: number;
  event_id?: string;
}

export interface AccidentEventPayload {
  type: 'accident';
  timestamp: number;
  edge_id: string;
  capacity_reduction?: number;
  duration?: number;
  event_id?: string;
}

export interface RoadClosureEventPayload {
  type: 'road_closure';
  timestamp: number;
  target: string;
  duration?: number;
  event_id?: string;
}

export interface EmergencyArrivalEventPayload {
  type: 'emergency_arrival';
  timestamp: number;
  vehicle_id?: string;
  origin?: string;
  destination?: string;
  emergency_subtype?: string;
  priority_weight?: number;
  event_id?: string;
}

export type EventInjectPayload =
  | CongestionSpikeEventPayload
  | AccidentEventPayload
  | RoadClosureEventPayload
  | EmergencyArrivalEventPayload;

export interface WebSocketMessage {
  type: 'state' | 'metrics' | 'signal_update' | 'event' | 'optimization' | 'emergency' | 'completed' | 'error';
  timestamp: number;
  data: Record<string, unknown>;
}

export type WebSocketConnectionStatus = 'CONNECTING' | 'LIVE' | 'PAUSED' | 'DISCONNECTED' | 'ERROR';
