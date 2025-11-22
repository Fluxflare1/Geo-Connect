Here’s the full content for docs/architecture/04-scaling-strategy.md.


---

04 – Scaling Strategy

1. Purpose

This document describes how Geo-Connect scales from:

A single-region, early deployment
→ to

A multi-region, multi-tenant, multi-provider MaaS platform capable of serving hundreds of millions of users and devices across Nigeria and other African countries.


The goal is to:

Keep the core architecture stable

Introduce scaling in phases

Avoid premature complexity

Ensure that each phase is operationally realistic


This is not a step-by-step deployment guide but a strategic roadmap for capacity and reliability.


---

2. Targets & Assumptions

2.1 Functional targets

Geo-Connect must support:

One unified Customer App for all passengers:

Taxi, ride-hailing, scheduled buses, intercity coaches, trains, ferries, school buses, corporate shuttles.


Many providers:

Public & private operators, schools, companies.


Multi-tenant white-labeling:

Some tenants use the “Geo-Connect” brand, others use their own.



2.2 Scale assumptions

The architecture must be able to evolve to:

Users: 100M+ in Nigeria, 500M+ across Africa

Providers: Thousands of operators

Vehicles/fleets: Tens or hundreds of millions of vehicles (over time)

Bookings & tickets:

Millions of bookings per day

Peaks around commute times and holidays



2.3 Non-functional goals

High Availability (HA) – especially for core APIs (search, booking, payment, ticket validation).

Horizontal scalability – scale by adding nodes/regions, not rewriting core logic.

Vendor and cloud agnostic – able to run on any Kubernetes-compatible platform.

Security & isolation – per-tenant and per-provider data boundaries.



---

3. Scaling Phases Overview

Scaling is broken into phases:

1. Phase 0 – Developer / Local


2. Phase 1 – Single Region, Simple HA


3. Phase 2 – Optimized Single Region (Caching & Read Replicas)


4. Phase 3 – Partitioning & Segmentation by Tenant/Region


5. Phase 4 – Multi-Region Deployment (Africa-wide)


6. Phase 5 – Extreme Scale & Specialized Services (Optional)



Each phase builds on the previous without breaking the logical architecture.


---

4. Phase 0 – Developer / Local

4.1 Context

Used for development & QA only.

Not for production traffic.

Focus: feature development, testing, stable APIs.


4.2 Infra

docker-compose in infra/docker-compose.yml:

1× Postgres

1× Redis

1× Django backend

1× Nginx

1× Customer App (Next.js dev server)


No Kubernetes; minimal setup.


4.3 Data & capacity

A single database instance.

Suitable for:

Few developers

Test data in thousands of rows



4.4 Observability

Simple logging to console.

Optional: local Prometheus/Grafana stack for dev experimentation.



---

5. Phase 1 – Single Region, Simple HA

5.1 Context

First real production deployment, e.g. Nigeria-only pilot:

Initial providers (1–10)

Tens to hundreds of thousands of users

Hundreds to thousands of daily bookings


5.2 Infra

Kubernetes cluster for backend/ + frontend/:

2–3 replicas of backend API (geo_connect + apps)

2–3 replicas of customer app (Next.js)

Nginx/ingress controller as reverse proxy and TLS termination


Single Postgres (managed or self-hosted) with:

Daily backups

Basic monitoring



5.3 Logical services

All backend apps run in the same Django project:

iam, tenancy, providers, catalog, trip_planning

booking, ticketing, pricing, payments, wallet (optional)

notifications, integrations, analytics, settlement


5.4 Capacity & limits

Likely comfortable up to:

Low millions of users

Tens of thousands of daily bookings


Bottlenecks:

Single DB write throughput

No read replicas

Bursty workloads (peaks) might cause latency spikes



5.5 Observability

Central logging (e.g. ELK / Loki).

Basic metrics:

Request rate

Error rate

Latency (P50/P95)


Health checks & alerts (CPU, memory, DB connectivity).



---

6. Phase 2 – Optimized Single Region (Caching & Read Replicas)

6.1 Context

Deployment still in one region (e.g. Lagos data center), but traffic grows:

Millions of users

Hundreds of thousands of daily bookings

Multiple large providers onboarded


6.2 Infra improvements

Postgres:

1 write master

1–N read replicas

Automatic failover configured via managed service or tooling.


Redis:

Introduced for:

Caching (trip search results, fare estimates)

Session throttling

Rate limiting



Horizontal scaling:

Backend pods autoscale based on CPU/RAM/requests.

Frontend pods autoscale for peak web load.



6.3 Application optimizations

Caching strategy:

Cache static catalog data (routes, stops, schedules) in Redis.

Cache search results and fare estimates with short TTL.


Read/write separation:

Read-heavy operations (search, trip history, reporting) use read replicas.

Write-heavy operations (booking, payment, ticket issuance) go to master.


Queuing:

Introduce a message queue (e.g. RabbitMQ, Kafka, SQS) for:

Notifications (SMS, email)

Analytics ingestion

Heavy background tasks (e.g. full-day settlement runs)




6.4 Capacity & limits

Capable of serving:

Millions of users in one country comfortably.

High bursts in morning/evening peaks with proper autoscaling.


Still primarily single-region:

Latency is okay for users near the region.

Cross-country access may have higher latency but still acceptable.




---

7. Phase 3 – Partitioning & Segmentation by Tenant/Region

7.1 Context

Geo-Connect begins to unify multiple regions in Nigeria and possibly first external markets:

Many providers

Many cities (Lagos, Abuja, Port Harcourt, etc.)

Increasing number of bookings and trips


7.2 Data partitioning strategy

Introduce logical boundaries in data:

Partition key candidates:

tenant_id

region

provider_id



Techniques:

1. Table partitioning inside Postgres:

Partition high-volume tables:

bookings

tickets

vehicle_positions (if stored)


Partition by region or tenant.



2. Schema-per-tenant (for very large tenants):

For extremely big operators, allocate separate schema or database.

Still share the same application code.



3. Read models for analytics:

Offload analytics data to a data warehouse (BigQuery, Redshift, Snowflake, etc.).

Keep operational DB focused on current transactions.




7.3 Service segmentation

Organizationally (still one Django project, but with internal boundaries):

High-traffic domains can be deployed with more replicas:

booking, payment, trip_planning


Low-traffic domains (like settlement, analytics) can run fewer replicas.


We can also start planning the option of splitting out some services later (Phase 5) if necessary.

7.4 Capacity & limits

Geo-Connect can now support:

Multiple large cities

Very large operators

Millions of daily requests



The main limitations become:

Multi-region latency (if users are far from the single main region)

Regulatory requirements for data residency in other countries



---

8. Phase 4 – Multi-Region Deployment (Africa-Wide)

8.1 Context

Geo-Connect expands beyond Nigeria:

Multiple countries (e.g. Ghana, Kenya, South Africa, etc.).

Data residency and latency requirements by region.

Very high number of users and daily operations.


8.2 Region strategy

Deploy separate clusters per region, for example:

africa-west-1 – handles Nigeria, Ghana

africa-east-1 – handles Kenya, Tanzania

africa-south-1 – handles South Africa, neighboring countries


Each region has:

Its own Kubernetes cluster

Its own primary Postgres cluster

Its own Redis and queues

Local Nginx/ingress and CDN edges


8.3 Tenant/region mapping

Each tenant is assigned a primary region.

DNS / routing layer ensures:

Customer app requests go to the nearest relevant region.

API gateway uses tenant/host to route to the correct region.



8.4 Data model for cross-region

Per-region data isolation:

Bookings, tickets, trip data are stored regionally.

Only summary/aggregated data is replicated centrally for global analytics.


Global identity & directory via iam + tenancy:

Option A: Users exist per region.

Option B: Global user identities with region-affinity for operations.



8.5 Consistency vs Availability

For bookings and payments within a region, we preserve strong consistency.

Across regions:

Analytics and reporting can be eventually consistent.

Cross-region provider operations (rare) need careful design.



8.6 Capacity

At this stage, the platform capacity scales roughly linearly with:

Number of regions

Provisioned infra per region


With enough resources, it can support:

Hundreds of millions of users across regions

Massive number of vehicles and providers

High-volume daily bookings continent-wide



---

9. Phase 5 – Extreme Scale & Specialized Services (Optional)

9.1 Context

Reserved for when Geo-Connect hits extremely high scale:

National adoption in multiple countries

Partnerships with government/public transport

Daily transactions in tens or hundreds of millions


9.2 Service extraction

Certain high-load concerns can be split into specialized services:

Real-time location & events:

Separate real-time service (e.g. on top of Kafka/stream processing).


Search & Trip Planning:

Dedicated trip-planning service with its own optimization and caching layers.


Pricing & Dynamic fare computation:

High-performance service for surge/dynamic pricing.



These services still use the same logical domains, just deployed as independent, highly optimized components (possibly in different languages where helpful, e.g. Go/Rust for some hot paths).

9.3 Advanced patterns

Event sourcing for critical domains (optional)

CQRS (Command Query Responsibility Segregation) for high-read workloads

Global traffic steering with smart routing (per-tenant, per-region, per-mode)



---

10. Operational Considerations Across All Phases

Regardless of phase, the following are critical:

10.1 Observability

Centralized logging by service & tenant

Metrics dashboards:

Request rate (RPS)

Latency (P50/P95/P99)

Error rate

Booking success rate

Payment success/failure


Tracing for critical flows:

Search → Booking → Payment → Ticket



10.2 SLOs (Service Level Objectives)

Example SLOs:

99.9% availability for:

Booking APIs

Ticket validation


99% availability for:

Trip search

Notifications



10.3 Security & Compliance

Tenant-level data separation

Secure storage of secrets & keys

Compliance with local regulations:

Data residency

KYC/AML (if required by payment regulations)




---

11. Summary

Geo-Connect’s logical architecture (apps: iam, tenancy, providers, booking, ticketing, payments, integrations, etc.) is already structured for scale.

Capacity is determined by how we deploy and evolve infra through the phases, not by a fixed hard-coded limit.

This roadmap outlines a clear path:

from single-region Nigeria pilot
→ to a nationwide, then continent-wide MaaS backbone
→ with the ability to onboard many providers and support hundreds of millions of users.



This document should be reviewed and refined as real usage data, growth patterns, and regulatory requirements emerge.
