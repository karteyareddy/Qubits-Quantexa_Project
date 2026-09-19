/**
 * Cohesive Metropolitan City Map topology, street signage, and district definitions.
 * Provides realistic, clean municipal names without AI buzzwords or conflicting regions.
 */

export interface CityIntersection {
  id: string;
  code: string;
  name: string;
  crossStreet: string;
  district: string;
  landmark: string;
  x: number;
  y: number;
  speedLimit: string;
}

export const CITY_INTERSECTIONS: Record<string, CityIntersection> = {
  I1: {
    id: 'I1',
    code: 'I1',
    name: 'West Gateway & 1st Ave',
    crossStreet: 'Grand Pkwy × 1st Ave N',
    district: 'Northwest Transit Hub',
    landmark: 'Grand Regional Transit Terminal',
    x: 135,
    y: 110,
    speedLimit: '45 km/h',
  },
  I2: {
    id: 'I2',
    code: 'I2',
    name: 'Grand Central & Broadway',
    crossStreet: 'Grand Pkwy × Broadway',
    district: 'Civic Center & City Hall',
    landmark: 'Metropolitan City Hall & Plaza',
    x: 435,
    y: 110,
    speedLimit: '50 km/h',
  },
  I3: {
    id: 'I3',
    code: 'I3',
    name: 'Financial Plaza & 8th Ave',
    crossStreet: 'Grand Pkwy × 8th Ave',
    district: 'Financial District',
    landmark: 'Metropolitan Exchange & Commercial Center',
    x: 735,
    y: 110,
    speedLimit: '50 km/h',
  },
  I4: {
    id: 'I4',
    code: 'I4',
    name: 'Tech Boulevard & 1st Ave',
    crossStreet: 'Ocean Blvd × 1st Ave N',
    district: 'Innovation Corridor',
    landmark: 'Tech Innovation & Research Park',
    x: 135,
    y: 350,
    speedLimit: '45 km/h',
  },
  I5: {
    id: 'I5',
    code: 'I5',
    name: 'Market Square & Broadway',
    crossStreet: 'Ocean Blvd × Broadway',
    district: 'Downtown Shopping Core',
    landmark: 'Market Square & Rail Station',
    x: 435,
    y: 350,
    speedLimit: '40 km/h',
  },
  I6: {
    id: 'I6',
    code: 'I6',
    name: 'Harbor Terminal & 8th Ave',
    crossStreet: 'Ocean Blvd × 8th Ave',
    district: 'Maritime Port District',
    landmark: 'Harbor Terminal & Ferry Pier',
    x: 735,
    y: 350,
    speedLimit: '60 km/h',
  },
};

export const ROAD_SIGN_NAMES: Record<string, { name: string; shield: string; lanes: number }> = {
  'I1-I2': { name: 'Grand Parkway (Route 10 West)', shield: '10', lanes: 2 },
  'I2-I1': { name: 'Grand Parkway (Route 10 West)', shield: '10', lanes: 2 },
  'I2-I3': { name: 'Grand Parkway (Route 10 East)', shield: '10', lanes: 2 },
  'I3-I2': { name: 'Grand Parkway (Route 10 East)', shield: '10', lanes: 2 },
  'I4-I5': { name: 'Ocean Boulevard (Route 20 West)', shield: '20', lanes: 2 },
  'I5-I4': { name: 'Ocean Boulevard (Route 20 West)', shield: '20', lanes: 2 },
  'I5-I6': { name: 'Ocean Boulevard (Route 20 East)', shield: '20', lanes: 2 },
  'I6-I5': { name: 'Ocean Boulevard (Route 20 East)', shield: '20', lanes: 2 },
  'I1-I4': { name: '1st Avenue North', shield: '1ST', lanes: 2 },
  'I4-I1': { name: '1st Avenue North', shield: '1ST', lanes: 2 },
  'I2-I5': { name: 'Broadway Central Corridor', shield: 'BWY', lanes: 2 },
  'I5-I2': { name: 'Broadway Central Corridor', shield: 'BWY', lanes: 2 },
  'I3-I6': { name: '8th Avenue Harbor Expressway', shield: '8TH', lanes: 3 },
  'I6-I3': { name: '8th Avenue Harbor Expressway', shield: '8TH', lanes: 3 },
};
