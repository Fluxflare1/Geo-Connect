# Geo-Connect Logical Architecture

Geo-Connect is a multi-tenant, white-label Mobility-as-a-Service (MaaS) platform that connects:

- **Passengers (Customers)** – using the Customer App (web & mobile).
- **Service Providers (Operators)** – using the Provider Portal.
- **Platform Admins** – using the Admin Console.

Under the hood, the platform is organised into clear domains (Django apps) that work together but remain loosely coupled.

---

## 1. Core Domains

### 1.1 IAM (`apps.iam`)

**Responsibility:** Identity & Access Management for all human users (customers, provider staff, admins).

Key responsibilities:

- User accounts (email/password, profile, roles).
- Authentication (JWT or similar).
- Authorisation (roles and permissions).
- Session & security features (password change/reset).

Key model concepts (simplified):

- `User`
- `Role`
- `Permission`
- (Optional) `UserRole`, `RolePermission`

Key API endpoints (examples):

- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `PATCH /api/v1/auth/me`
- `POST /api/v1/auth/change-password`
- `POST /api/v1/auth/forgot-password`
- `POST /api/v1/auth/reset-password`

IAM does **not** care about transport or mobility directly. It only knows **who** the user is and **what** they are allowed to do.

---

### 1.2 Tenancy (`apps.tenancy`)

**Responsibility:** Multi-tenant separation and routing.

Key responsibilities:

- Tenants (brands / organisations using Geo-Connect).
- Tenant domains (e.g. `brand-a.geoconnect.com`).
- Region mapping (which cluster/region serves the tenant).

Typical concepts:

- `Tenant` – top-level organisation.
- `TenantDomain` – domain to route requests.
- `TenantRegion` – which region/cluster serves the tenant.

Every request is associated with exactly one **tenant**, via:

- Domain mapping, and/or
- Header such as `X-Tenant-ID`.

Tenancy ties into:

- **Branding** – for white-label theming.
- **Providers** – providers are usually scoped under tenants.
- **Config** – integration keys, feature flags per tenant.

---

### 1.3 Branding (`apps.branding`)

**Responsibility:** White-label look & feel per tenant or provider.

Key responsibilities:

- Colors, logos, fonts.
- White-label settings: app name, favicon, etc.
- Customer App theming.

Typical concepts:

- `BrandTheme` – theme linked to `Tenant` or `Provider`.

The frontend (Customer App, Provider Portal) reads branding settings and applies them so that the same codebase can show different brands.

---

### 1.4 Providers (`apps.providers`)

**Responsibility:** Onboard and manage **Service Providers** (operators).

Key responsibilities:

- Provider records (bus companies, ferry operators, taxi fleets, etc.).
- Service types per provider (FIXED_ROUTE, ON_DEMAND, SHUTTLE, CHARTER, etc.).
- Operational status (active, suspended).
- Integration bindings (which PSP, SMS provider, etc., to use for that provider).

Typical concepts:

- `Provider` – an operator.
- `ProviderServiceType` – what kind of services the provider runs.
- `ProviderIntegrationConfig` – mapping to integration configs (e.g. which payment gateway).

Providers connect to:

- **Catalog** – provider’s routes and products.
- **Trip Planning** – which services are available.
- **Settlements** – which provider gets which payouts.
- **Integrations** – which vendor implementation to call for that provider.

---

### 1.5 Catalog (`apps.catalog`)

**Responsibility:** Static or semi-static **service definitions**.

Key responsibilities:

- Stops (stations, terminals, piers, bus stops).
- Routes (origin–destination).
- Trips (services operated at specific times).
- Modes (BUS, TRAIN, FERRY, TAXI, etc.).
- Products (economy, VIP, sleeper, etc.).

Typical concepts:

- `Stop`
- `Route`
- `TripTemplate` / `TripInstance`
- `Mode` / `Product`

Catalog feeds **Trip Planning** and **Booking**.

---

### 1.6 Trip Planning (`apps.trip_planning`)

**Responsibility:** Search & routing for MaaS.

Key responsibilities:

- Search for available trips based on:
  - origin, destination, time, mode(s), provider(s).
- Compute itineraries and options (direct, multi-leg).
- Integrate with **real-time** updates (delays, cancellations).

Typical concepts:

- `TripOption` (computed result, not necessarily a stored model).
- Search APIs:
  - `GET /api/v1/trips/search`

Trip Planning uses:

- **Catalog** for static routes/timetables.
- **Realtime** for current status.
- **Pricing** to attach fare estimates.

---

### 1.7 Booking (`apps.booking`)

**Responsibility:** Booking lifecycle.

Key responsibilities:

- Reservations (pending payment).
- Confirmed bookings.
- Cancellations, expiries, and state transitions.
- Linking bookings to:
  - Customer (`User`)
  - Provider (`Provider`)
  - Trip (from `catalog`/`trip_planning`)

Typical concepts:

- `Booking`
- `BookingPassenger`
- `BookingStatus` (PENDING_PAYMENT, CONFIRMED, CANCELLED, EXPIRED, FAILED)

Key APIs:

- `POST /api/v1/bookings` – create booking.
- `GET /api/v1/bookings` – list bookings for the logged-in user.
- `GET /api/v1/bookings/{id}` – booking details.
- `POST /api/v1/bookings/{id}/cancel` – request cancellation.

Booking is the core object connecting customers to trips.

---

### 1.8 Ticketing (`apps.ticketing`)

**Responsibility:** Tickets and validation.

Key responsibilities:

- Generate ticket codes and QR payloads.
- Associate tickets to passengers and bookings.
- Check-in / validation API for provider scanners.
- Ticket validity windows.

Typical concepts:

- `Ticket`
- `TicketStatus` (ISSUED, USED, EXPIRED, CANCELLED)

Ticketing listens to **Booking** events (e.g. booking confirmed, cancelled) and creates or updates tickets accordingly.

---

### 1.9 Pricing (`apps.pricing`)

**Responsibility:** Fare calculation and rules.

Key responsibilities:

- Base tariffs per route/mode/product.
- Dynamic pricing rules (peak/off-peak, demand-based).
- Promotions and discount rules.

Typical concepts:

- `Tariff`
- `PricingRule`
- `Promotion`

Trip Planning queries Pricing to present **fare estimates**.

Booking calls Pricing to compute **final payable amount** at booking time.

---

### 1.10 Payments (`apps.payments`) & Wallet (`apps.wallet`, optional)

**Responsibility:** Platform-level payment flows.

Key responsibilities:

- Payment intents and status (INITIATED, SUCCESS, FAILED).
- Payment sessions passed to frontend (redirect URLs, references).
- Mapping between bookings, payment providers, and transactions.
- (Optional) Wallet balances / stored value for customers and providers.

Payments does **not** talk directly to Paystack/Stripe/Flutterwave.  
Instead it uses **Integrations → Payments** (see below).

---

### 1.11 Notifications (`apps.notifications`)

**Responsibility:** High-level messaging (SMS, email, push) without vendor lock.

Key responsibilities:

- Notification templates (booking confirmation, ticket issued, password reset).
- Routing to channels (email, SMS, push).
- Calling the appropriate **integration** implementation at runtime.

Typical concepts:

- `NotificationTemplate`
- `NotificationLog`

Notifications knows **what** to send and **to whom**, but not **how** a specific vendor sends it.

For **how**, it delegates to `apps.integrations`.

---

### 1.12 Realtime (`apps.realtime`)

**Responsibility:** Real-time events and positions.

Key responsibilities:

- Vehicle locations (GPS, IoT feeds).
- Real-time trip status (on time, delayed, cancelled).
- Event distribution to customers and providers.

Realtime integrates with:

- Trip Planning (e.g. show live delay).
- Customer App (live maps).
- Provider Portal (operations view).

---

### 1.13 Analytics (`apps.analytics`)

**Responsibility:** Aggregated metrics & reporting.

Key responsibilities:

- Usage metrics (searches, bookings, conversion).
- Revenue per provider, route, mode.
- Operational KPIs (on-time performance, cancellations, etc.).

Analytics reads from Booking, Payments, Realtime, etc., and exposes reports to the Admin Console and Provider Portal.

---

### 1.14 Support (`apps.support`)

**Responsibility:** Customer support tickets & conversations.

Key responsibilities:

- Ticket lifecycle (OPEN, IN_PROGRESS, RESOLVED, CLOSED).
- Message threads between customer & agent.
- Linking tickets to bookings, providers, or trips.

Key APIs:

- `GET /api/v1/support/tickets`
- `POST /api/v1/support/tickets`
- `GET /api/v1/support/tickets/{id}`
- `POST /api/v1/support/tickets/{id}/messages`

---

### 1.15 Settlement (`apps.settlement`)

**Responsibility:** Provider settlement & payouts.

Key responsibilities:

- Calculate provider shares per trip/booking.
- Group into settlement batches.
- Handle payout workflow.

This is where platform fees and revenue-sharing rules are applied.

---

### 1.16 Core (`apps.core`) & Config (`apps.config`)

**Responsibility:** Shared infrastructure concerns.

- `core`:
  - Idempotency keys, audit logging, request IDs, error handling.
- `config`:
  - Configuration models and feature flags which:
    - hold which integrations/vendors are enabled,
    - configure defaults and thresholds.

Typical concepts:

- `IntegrationConfig` (could live in `config` or `providers`).
- `FeatureFlag`

---

## 2. Integrations Layer (`apps.integrations`)

**Goal:** Vendor-neutral architecture for external services.

The `integrations` package defines **interfaces**, not business logic.

```text
apps.integrations
├── maps/
│   ├── base.py          # MapProvider interface
│   ├── google_maps.py
│   ├── mapbox.py
│   └── openstreetmap.py
├── payments/
│   ├── base.py          # PaymentProvider interface
│   ├── paystack.py
│   ├── flutterwave.py
│   └── stripe.py
├── sms/
│   ├── base.py          # SmsProvider interface
│   ├── twilio.py
│   ├── termii.py
│   └── africastalking.py
└── email/
    ├── base.py          # EmailProvider interface
    ├── sendgrid.py
    └── ses.py
