Here’s the Trip Search section you can drop into
docs/api-specs/customer-api.md.

I’ll assume that file already exists with some intro; you can append this under a new heading like ## Trip Search & Discovery.


---

## Trip Search & Discovery

These endpoints power the customer trip search and selection flow:

1. `POST /api/v1/trips/search` – search for available trips/offers  
2. `GET  /api/v1/trips/{trip_id}/summary` – fetch summary for a selected trip (used by checkout)

All endpoints are **tenant-aware** and **authenticated** (`Bearer` token), unless otherwise noted.

---

### 1. POST /api/v1/trips/search

Search for available trips or offers between an origin and destination on a given date/time.

**URL**

```http
POST /api/v1/trips/search

Auth

Required: Authorization: Bearer <access-token>

Tenant inferred from domain or X-Tenant header.


Headers

Authorization: Bearer <token>
Content-Type: application/json
X-Tenant: <tenant-slug>           # optional if inferred from domain
X-Request-Id: <uuid>              # optional, for tracing

Request body

{
  "origin": {
    "type": "STOP_ID",
    "value": "lagos-jibowu-terminal"
  },
  "destination": {
    "type": "STOP_ID",
    "value": "abuja-utako-terminal"
  },
  "departure_date": "2025-12-01",
  "departure_time": "morning",
  "passengers": 1,
  "mode": "ANY",
  "filters": {
    "providers": [],
    "max_price": null,
    "direct_only": false
  },
  "sort_by": "DEPARTURE_TIME",
  "sort_order": "ASC"
}

Field details

origin

type: "STOP_ID" | "CITY_CODE" | "COORDINATES"

value:

STOP_ID: platform stop identifier (e.g. "lagos-jibowu-terminal")

CITY_CODE: city identifier (e.g. "LAGOS", "ABUJA")

COORDINATES: future support for lat/lng (e.g. "6.5244,3.3792")



destination

Same structure as origin.


departure_date (string, YYYY-MM-DD)

Customer’s intended departure date (local time).


departure_time (string)

"ANY" | "MORNING" | "AFTERNOON" | "EVENING" | "NIGHT" | specific time "HH:MM"

For v1, recommended values: "ANY" or "MORNING" | "AFTERNOON" | "EVENING".


passengers (integer)

Number of seats requested. Default 1. Must be ≥ 1.


mode (string)

"ANY" – return all supported modes.

"BUS" – scheduled buses/coaches/intercity.

"RAIL" – trains.

"FERRY" – boats/ferries.

"TAXI" – on-demand taxi/ride-hailing.

"SHUTTLE" – shared shuttles/school/enterprise transport.


filters (object, optional)

providers: array of provider IDs to include (empty = all).

max_price: maximum total price (numeric) for requested passengers.

direct_only: boolean – true to exclude multi-leg journeys.


sort_by (string)

"DEPARTURE_TIME" | "PRICE" | "ARRIVAL_TIME" | "DURATION"


sort_order (string)

"ASC" | "DESC".



If any optional field is omitted, sensible defaults are applied:

{
  "mode": "ANY",
  "filters": {
    "providers": [],
    "max_price": null,
    "direct_only": false
  },
  "sort_by": "DEPARTURE_TIME",
  "sort_order": "ASC"
}


---

Successful response (200)

{
  "search_id": "e0b4e7fa-0a9c-4ba0-9ae6-02c0f7f7a9ac",
  "currency": "NGN",
  "results": [
    {
      "trip_id": "TRIP_20251201_LAGOS_JIBOWU_ABUJA_UTAKO_001",
      "provider": {
        "id": "PROV_GIGM",
        "name": "GIGM",
        "logo_url": "https://cdn.example.com/providers/gigm.png",
        "rating": 4.5
      },
      "mode": "BUS",
      "product_type": "INTERCITY",
      "origin": {
        "stop_id": "lagos-jibowu-terminal",
        "name": "Jibowu Terminal",
        "city_code": "LAGOS"
      },
      "destination": {
        "stop_id": "abuja-utako-terminal",
        "name": "Utako Terminal",
        "city_code": "ABUJA"
      },
      "departure_time": "2025-12-01T08:30:00+01:00",
      "arrival_time": "2025-12-01T17:00:00+01:00",
      "duration_minutes": 510,
      "available_seats": 12,
      "price": {
        "currency": "NGN",
        "total": 15000.0,
        "per_passenger": 15000.0,
        "fees_included": true
      },
      "constraints": {
        "refundable": true,
        "changeable": true,
        "baggage_included": true,
        "checkin_required": false
      },
      "tags": ["AC_BUS", "SNACKS", "CHARGING_PORTS"],
      "preview": {
        "vehicle_type": "55-seater coach",
        "route_label": "Lagos → Abuja (Express)",
        "badge": "Popular",
        "primary_color": "#0044CC"
      }
    }
  ]
}

Field details

search_id

Server-generated UUID representing this search.

Can be used for analytics or re-fetching results if needed.


currency

Default currency for prices in this response (e.g. "NGN").


results[]

trip_id

Opaque identifier used later in:

GET /api/v1/trips/{trip_id}/summary

POST /api/v1/bookings (booking creation).



provider

id: provider code or UUID.

name: display name.

logo_url: optional logo to display in the app.

rating: optional aggregated rating.


mode

"BUS" | "RAIL" | "FERRY" | "TAXI" | "SHUTTLE" | "OTHER".


product_type

High-level product label for UI:

"INTERCITY" – city-to-city.

"CITY_BUS" – intra-city bus.

"RIDE_HAIL" – taxi/ride-hailing.

"SCHOOL" – school bus.

"CORPORATE" – enterprise shuttle.

etc.



origin, destination

stop_id: internal stop identifier.

name: human-readable name.

city_code: optional city code.


departure_time, arrival_time

ISO 8601 timestamps with timezone offset.


duration_minutes

Suggested duration for the trip in minutes.


available_seats

Seats currently available for booking for this trip (if applicable; for taxi, this might be null or 1).


price

currency: e.g. "NGN".

total: total for the number of passengers requested.

per_passenger: single passenger price.

fees_included: whether all mandatory fees are included.


constraints

Business rules relevant to booking:

refundable: can this ticket be refunded?

changeable: can date/time be changed?

baggage_included: includes standard baggage.

checkin_required: requires check-in before boarding.



tags

Optional UI tags/labels (e.g. "AC_BUS", "NON_STOP", "WIFI").


preview

Optional UI hints:

vehicle_type: e.g. "Sedan", "Coaster", "55-seater coach".

route_label: short label for route.

badge: e.g. "Popular", "Cheapest", "Fastest".

primary_color: provider or line color, hex.






---

Error responses

400 Bad Request

Invalid origin/destination, date format, or passengers count.


401 Unauthorized

Missing or invalid token.


404 Not Found

No trips found for the given criteria (can also return 200 with results: [], depending on API design preference).


500 Internal Server Error

Unexpected failure on server side.



Example no-results response (preferred):

{
  "search_id": "8b3a2a7a-ae45-4ccf-9e24-d8a3a355b0d1",
  "currency": "NGN",
  "results": []
}


---

2. GET /api/v1/trips/{trip_id}/summary

Retrieve a stable summary for a single trip, used by the checkout page before creating a booking.

URL

GET /api/v1/trips/{trip_id}/summary

Auth

Required: Authorization: Bearer <access-token>


Headers

Authorization: Bearer <token>
X-Tenant: <tenant-slug>           # optional if inferred from domain
X-Request-Id: <uuid>              # optional

Path parameters

trip_id – the opaque ID returned by POST /trips/search.



---

Successful response (200)

{
  "trip_id": "TRIP_20251201_LAGOS_JIBOWU_ABUJA_UTAKO_001",
  "provider": {
    "id": "PROV_GIGM",
    "name": "GIGM",
    "logo_url": "https://cdn.example.com/providers/gigm.png"
  },
  "mode": "BUS",
  "product_type": "INTERCITY",
  "origin": {
    "stop_id": "lagos-jibowu-terminal",
    "name": "Jibowu Terminal",
    "city_code": "LAGOS"
  },
  "destination": {
    "stop_id": "abuja-utako-terminal",
    "name": "Utako Terminal",
    "city_code": "ABUJA"
  },
  "departure_time": "2025-12-01T08:30:00+01:00",
  "arrival_time": "2025-12-01T17:00:00+01:00",
  "duration_minutes": 510,
  "available_seats": 12,
  "currency": "NGN",
  "total_price": 15000.0,
  "per_passenger_price": 15000.0,
  "fare_rules": {
    "refundable": true,
    "changeable": true,
    "refund_penalty_percent": 10,
    "change_penalty_percent": 5,
    "latest_change_deadline": "2025-11-30T23:59:59+01:00",
    "latest_refund_deadline": "2025-11-30T23:59:59+01:00"
  }
}

This summary is what the Customer App checkout page uses to:

Display trip details.

Confirm price and available seats.

Prepare POST /bookings payload.



---

Error responses

400 Bad Request

Invalid trip_id format.


401 Unauthorized

Missing/invalid token.


404 Not Found

Trip does not exist or is not available (expired or sold out).


410 Gone

Optional: trip existed but is no longer available (expired or cancelled).



Example 404:

{
  "detail": "Trip not found or no longer available."
}


---

3. Relationship with Bookings

Once a trip is selected:

1. Customer App calls GET /trips/{trip_id}/summary.


2. Customer confirms passenger details on the checkout page.


3. Customer App calls:



POST /api/v1/bookings

With body referencing trip_id and passenger details.
Booking creation, payment session, and ticketing are covered in the Bookings & Payments section of this document.


---

That’s the full Trip Search API spec needed for the Customer App to do:

> Search → see results → select one → show summary → continue to checkout



Next logical step (when you’re ready) is:

Implement these endpoints in Django trip_planning + catalog (backend),

Then wire the Next.js /search UI to POST /trips/search and use this schema.
