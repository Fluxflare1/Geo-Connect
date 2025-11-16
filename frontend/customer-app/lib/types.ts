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

export interface SupportMessage {
  id: string;
  sender_type: "CUSTOMER" | "AGENT" | "SYSTEM";
  sender_name?: string;
  body: string;
  internal_only: boolean;
  created_at: string;
}

export interface SupportTicket {
  id: string;
  subject: string;
  category: "BOOKING" | "PAYMENT" | "TRIP" | "ACCOUNT" | "OTHER";
  status: "OPEN" | "IN_PROGRESS" | "RESOLVED" | "CLOSED";
  priority: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  booking_id?: string | null;
  provider_id?: string | null;
  created_at: string;
  updated_at: string;
  last_activity_at: string;
  last_message?: {
    sender_type: string;
    body: string;
    created_at: string;
  } | null;
}

export interface SupportTicketDetail {
  id: string;
  subject: string;
  category: SupportTicket["category"];
  status: SupportTicket["status"];
  priority: SupportTicket["priority"];
  booking_id?: string | null;
  provider_id?: string | null;
  customer_user_id?: string | null;
  assigned_to_id?: string | null;
  created_at: string;
  updated_at: string;
  last_activity_at: string;
  messages: SupportMessage[];
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  phone_number?: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
}
