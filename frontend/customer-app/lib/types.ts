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


export interface BookingPassenger {
  id: string;
  passenger_type: string;
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
}

export interface Ticket {
  id: string;
  ticket_code: string;
  qr_payload: string;
  status: string;
  valid_from: string | null;
  valid_until: string | null;
}

export interface Booking {
  id: string;
  tenant: string;
  provider: string;
  trip: string;
  customer_user: string | null;
  status: string;
  reservation_expires_at: string | null;
  total_amount: number;
  currency: string;
  seats_count: number;
  metadata: Record<string, any>;
  passengers: BookingPassenger[];
  tickets: Ticket[];
  created_at: string;
  updated_at: string;
}

export interface PaymentSession {
  provider: string;
  payment_reference: string;
  redirect_url: string;
  callback_url: string;
  status: string;
}

export interface BookingCreateResponse {
  booking: Booking;
  payment_session: PaymentSession;
}
