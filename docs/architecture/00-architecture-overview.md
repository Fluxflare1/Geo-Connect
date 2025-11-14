# Geo-Connect – Architecture Overview

## 1. Introduction

Geo-Connect is a **multi-tenant, white-label, SaaS MaaS (Mobility as a Service) platform** that serves as a central hub for:

- Mobility management  
- Booking and ticketing  
- Trip planning and routing  
- Service provider onboarding and integration  
- Passenger-facing mobility services

It exposes:

- Public-facing web interfaces for **passengers**  
- White-label provider portals for **transport service providers**  
- An admin console for the **platform operator**  
- APIs and webhooks for **external integrations**

The system is designed from day one to support **global scale**, targeting the ability to handle **hundreds of millions of transactions across regions**.

---

## 2. Goals & Non-Goals

### 2.1 Core Goals

- **Multi-tenant SaaS**:  
  Support many independent providers/organizations on the same platform, with logical separation of data.

- **White-label capability**:  
  Each provider can have:
  - Custom branding (logo, colors, theme)  
  - Optional custom domain  
  - Customized configuration for payments, maps, notifications, etc.

- **High scalability & availability**:
  - Horizontal scale across multiple regions.
  - Architecture prepared for very high throughput (target: up to hundreds of millions of transactions across regions).

- **Pluggable integrations**:
  - Maps: Google Maps, Mapbox, OpenStreetMap, etc.  
  - SMS: Twilio, Termii, Africa’s Talking, etc.  
  - Payments: Stripe, Paystack, Flutterwave, etc.  
  - All done via **adapter interfaces** with configuration via API keys/placeholders.

- **API-first design**:
  - Backend exposes clean, documented APIs (REST/GraphQL) for:
    - Customer apps  
    - Provider integrations  
    - Admin and partner integrations

- **Modular services**:
  - Clear separation of concerns between identity, tenancy, catalog, booking, ticketing, payments, trip planning, notifications, integrations, and analytics.

### 2.2 Non-Goals (for now)

- Native mobile apps (Android/iOS) – can come later, built on top of the same APIs.
- Deep integration with city-wide public authority systems (optional future phase).
- Real-time IoT/vehicle telemetry – may integrate later but not in the first core.

---

## 3. High-Level Architecture

At a high level, Geo-Connect is composed of the following layers:

1. **Client & Presentation Layer**  
2. **API Gateway & Backend Application Layer**  
3. **Core Domain Services Layer (Django Apps)**  
4. **Integration & Adapters Layer**  
5. **Data & Storage Layer**  
6. **Infrastructure & Operations Layer**

### 3.1 Client & Presentation Layer

This layer contains **Next.js** applications:

- **Customer App (`frontend/customer-app/`)**
  - Public booking interface for passengers
  - Search, trip planning, booking, ticket viewing, wallet, profile
  - Multi-tenant aware via domain/host or tenant identifier

- **Provider Portal (`frontend/provider-portal/`)**
  - White-label interface for transport service providers
  - Route/trip management, capacity, pricing, bookings, reports, branding settings

- **Admin Console (`frontend/admin-console/`)**
  - Internal control center for the platform operator
  - Tenant management, provider management, global settings, monitoring, analytics

All frontends use:

- **Next.js** (SSR/ISR where appropriate)
- **TailwindCSS** and **shadcn-ui** for UI components
- Calls to backend APIs through a shared client library when possible

Frontends are typically served via **NGINX** and/or the Next.js runtime, behind a reverse proxy or load balancer.

---

### 3.2 API Gateway & Backend Application Layer

All frontends and external systems communicate with Geo-Connect via an **API gateway / reverse proxy** (e.g. NGINX, ingress controller).

- Routes traffic to:
  - **Django backend** (primary API server)
  - Static assets / Next.js frontends

The backend is a **Django** project (`backend/geo_connect/`) exposing:

- REST (via Django REST Framework) and/or GraphQL endpoints
- Multi-tenant and white-label aware endpoints
- Authentication and authorization (JWT, session-based, or token-based)

Key design principles:

- API-first: frontends consume the same public/internal APIs.
- Clear separation between **public** and **provider/admin** endpoints.
- Versioning support (e.g. `/api/v1/...`).

---

### 3.3 Core Domain Services (Django Apps)

The core business logic is implemented as modular Django apps inside `backend/apps/`:

- **tenancy/**  
  - Tenant/organization model (each provider/customer organization)
  - Domain mapping (custom domains, subdomains)
  - Tenant-aware middleware and routing
  - Isolation of data per tenant (row-level or schema-level, depending on strategy)

- **branding/**  
  - White-label configurations (logo, colors, theme, branding text)
  - Email/SMS template overrides per tenant
  - Frontend theme configs exposed via API

- **identity/**  
  - Users, roles, permissions (RBAC)
  - Authentication flows (login, registration, password management)
  - Support for different user types (passenger, provider user, admin)

- **providers/**  
  - Provider onboarding workflow
  - Provider configuration (payment settings, map provider preferences, limits)
  - Provider-level metadata (country, time zone, legal info)

- **catalog/**  
  - Modes of transport (bus, rail, taxi, ferry, etc.)
  - Routes, stops/stations, trips, schedules
  - APIs for listing/searching catalog data

- **booking/**  
  - Booking engine core:
    - Booking creation, states, passenger details
    - Capacity coordination
  - Integrates with pricing, payments, and ticketing services

- **ticketing/**  
  - Ticket generation (unique codes, QR/barcode payloads)
  - Ticket lifecycle: valid, used, expired, cancelled, refunded
  - Validation APIs for providers/operators

- **pricing/**  
  - Fare rules and tariffs
  - Dynamic pricing logic (optional/extendable)
  - Price calculation interfaces used by booking service

- **payments/**  
  - Unified payment abstraction layer
  - Wallet management (optional)
  - Handling of external payment gateway callbacks
  - Settlement and reconciliation data structures

- **trip_planning/**  
  - Trip search and (over time) multi-modal routing
  - Uses catalog data plus possible external map/route APIs
  - Exposes APIs for the customer app to query possible journeys

- **notifications/**  
  - Unified interface for email, SMS, push, in-app notifications
  - Uses specific adapters from the integrations layer
  - Templates that support per-tenant branding

- **integrations/**  
  - Maps: `maps/` (Google Maps, Mapbox, OSM, etc.)
  - Payments: `payments/` (Stripe, Paystack, Flutterwave, etc.)
  - SMS: `sms/` (Twilio, Termii, Africa’s Talking, etc.)
  - Each adapter implements a standard interface and is configured via environment variables or tenant-level settings.

- **analytics/**  
  - Aggregated reporting
  - KPIs per provider, per region, per route
  - Data exports and dashboards (consumed by Admin Console)

This modular approach supports:

- Clear boundaries
- Easier scaling of hot paths
- Independent evolution of domains

---

### 3.4 Integration & Adapters

Integration modules are designed using a **pluggable adapter pattern**:

- Each external service type (maps, payments, SMS) has:
  - A **base interface** (`base.py`)
  - Multiple concrete implementations
  - Configuration via:
    - Global env vars
    - Tenant/provider-specific config (e.g. which payment provider to use)

Examples:

- `backend/apps/integrations/maps/google_maps.py`
- `backend/apps/integrations/payments/stripe.py`
- `backend/apps/integrations/sms/twilio.py`

This allows Geo-Connect to:

- Run on **any hosting provider**
- Connect to **any approved third-party service**
- Switch providers without changing core business logic

---

## 4. Data & Storage Layer

Primary components:

- **PostgreSQL**
  - Main transactional database
  - Stores tenants, users, providers, catalog, bookings, tickets, payments, config
  - Multi-tenant strategy can be:
    - Single database + tenant key (row-level isolation), or
    - Schema-per-tenant (for stricter isolation)
  - To be detailed in `docs/data-model/`.

- **Redis** (recommended)
  - Caching (e.g. search results, configuration)
  - Session storage (optional)
  - Short-lived data: booking holds, rate limiting, queue info

- **Message Queue / Event Bus** (future/optional)
  - For large-scale async processing (notifications, analytics aggregation, etc.)

- **Data Warehouse / Analytics DB** (future/optional)
  - For heavy reporting and offline analytics

---

## 5. Infrastructure & Deployment

Baseline stack:

- **Docker**  
  - All services containerized:
    - `backend` (Django)
    - `frontend` apps (Next.js)
    - `PostgreSQL`
    - `Redis`
    - `NGINX`

- **NGINX**
  - Acts as:
    - Reverse proxy
    - Static asset server (if desired)
    - TLS termination (HTTPS)
    - Router for:
      - `/api/` → Django backend
      - `/` → appropriate frontend (customer/provider/admin based on host/path)

- **Environment Support**
  - Local dev (via `docker-compose`)
  - Staging
  - Production (on any cloud or VPS provider)

- **CI/CD (e.g. GitHub Actions)**
  - Build, test, and deploy Docker images
  - Run migrations and smoke tests

- **Multi-Region Design (High-Level)**
  - Deploy stacks to multiple regions (e.g. Region A, Region B)
  - Use DNS/load balancing to route users to nearest region
  - Data replication strategies (to be further detailed in `04-scaling-strategy.md`)

---

## 6. Scalability & Performance Direction

Geo-Connect must be designed to eventually handle **very high transaction volumes** (hundreds of millions across regions). At a high level, the architecture supports this by:

- Using **horizontal scaling** of:
  - Django application servers
  - Frontend servers
  - Databases (read replicas) and caches
- Keeping services **stateless** where possible
- Using **caching** and **asynchronous processing** for non-critical paths
- Planning evolution toward:
  - Sharding / partitioning strategies for bookings and tenants
  - Region-based deployments with local data residency
  - Dedicated infrastructure for high-load services (e.g. booking, payments)

Details of these strategies will be elaborated in:

- `docs/architecture/03-deployment-architecture.md`  
- `docs/architecture/04-scaling-strategy.md`

---

## 7. Security & Compliance (High-Level View)

- **Transport security**:  
  - Enforce HTTPS across all interfaces.

- **Authentication & Authorization**:
  - JWT or secure session-based auth
  - Role-based access control (RBAC) per tenant
  - Password hashing using industry standards

- **Multi-Tenancy Security**:
  - Every request is tenant-aware
  - Strict data isolation between tenants at the application layer (and optionally at DB layer)

- **Secrets & Keys**:
  - No hard-coded secrets
  - Use environment variables or secret managers for:
    - DB credentials
    - API keys (maps, SMS, payment providers)

- **Auditing & Logging**:
  - Store audit logs for critical actions:
    - Bookings, payments, cancellations, admin changes
  - Logs centralization and monitoring (e.g. ELK, cloud provider tools)

Further details will be provided in the security-specific documentation.

---

## 8. Next Steps

This document provides the **high-level architecture overview** for Geo-Connect.

The next documents will go deeper into:

- **System context and component diagrams**  
  (`docs/architecture/01-system-context.md`, `02-logical-architecture.md`)

- **Detailed SRS** per domain  
  (`docs/srs/01-srs-booking-ticketing.md`, etc.)

- **Data model** and table-level design  
  (`docs/data-model/02-booking-ticketing-tables.md`, etc.)

- **API specifications**  
  (`docs/api-specs/customer-api.md`, `provider-api.md`, `admin-api.md`, `webhooks.md`)

Geo-Connect will evolve iteratively, but this architecture baseline ensures that all future work aligns with:

- Multi-tenant SaaS  
- White-label support  
- High scalability across regions  
- Flexible integrations  
- API-first design
