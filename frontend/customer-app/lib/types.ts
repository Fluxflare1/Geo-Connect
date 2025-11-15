export interface FareComponent {
  type: string;
  amount: number;
}

export interface FareEstimate {
  currency: string;
  amount: number;
  components: FareComponent[];
}

export interface TripSegmentStop {
  id: string;
  name: string;
  lat: number;
  lng: number;
}

export interface TripSegment {
  segment_id: string;
  from_stop: TripSegmentStop;
  to_stop: TripSegmentStop;
  departure_time: string;
  arrival_time: string;
  vehicle_type: string;
  real_time_status: {
    status: string;
    delay_minutes: number;
  };
}

export interface TripSearchResult {
  id: string;
  provider_id: string;
  provider_name: string;
  mode: string;
  segments: TripSegment[];
  duration_minutes: number;
  total_distance_km: number;
  fare_estimate: FareEstimate;
  availability: {
    seats_total: number;
    seats_available: number;
  };
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    role: string;
  };
}
