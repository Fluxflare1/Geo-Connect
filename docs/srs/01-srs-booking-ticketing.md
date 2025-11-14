# Geo-Connect – Booking & Ticketing System SRS

## 1. Introduction

### 1.1 Purpose

This SRS specifies the functional and non-functional requirements for the **Booking & Ticketing Module** in the Geo-Connect MaaS platform.  
It defines how passengers search, reserve, book, pay, cancel, modify, and manage transportation services provided by multiple integrated transport operators.

This module is core to Geo-Connect and integrates with:

- Trip Planning & Routing  
- Payment & Wallet  
- Provider Integration Services  
- Notification Service  
- Multi-Tenancy Layer  
- Customer Experience Frontend  

### 1.2 Scope

The Booking & Ticketing Engine handles:

- Trip availability  
- Fare pricing  
- Seat or capacity allocation  
- Booking reservations  
- Payment & confirmation  
- Ticket generation  
- Booking lifecycle management  
- Provider reconciliation & reporting  
- Refunds & cancellations  

It must support high-throughput, multi-region, and multi-provider booking at massive scale.

### 1.3 Definitions

**Booking:** A confirmed transport reservation.  
**Reservation (Hold):** A temporary lock on seats before final payment.  
**Inventory:** Available seats or capacity on a specific service or trip.  
**PNR / Booking Reference:** Unique booking identifier.  
**Ticket:** Digital artifact (QR/Barcode/ID) issued after payment.  
**Trip:** A scheduled transport service (bus, train, ferry, etc.).  
**Segment:** Part of a multi-leg journey.  
**Provider:** A tenant operating transport services.

---

## 2. System Overview

The Booking & Ticketing Module consists of:

### 2.1 Core Components

- **Availability Engine**  
  Retrieves seat/capacity availability and route options.
  
- **Fare Engine**  
  Retrieves pricing, applies discounts, tenant rules, commissions, etc.
  
- **Reservation Engine**  
  Temporarily locks seats to avoid double-booking (uses Redis).

- **Booking Engine**  
  Finalizes each booking, confirms, and persists.

- **Ticket Generator**  
  Produces QR/Barcode tickets in provider or tenant format.

- **Booking Lifecycle Manager**  
  Handles modifications, cancellations, no-shows, expiries.

- **Provider Sync Engine**  
  Pushes bookings and cancellations to connected providers.

### 2.2 External Dependencies

- Payment Provider Adapters  
- SMS/Email Notification Adapters  
- Map Providers (indirect via trip planning)  
- Provider APIs (via integration layer)

---

## 3. Functional Requirements

---

# 3.1 Search & Availability

### FR-SEARCH-01  
Passengers shall be able to search for available trips using:

- Origin  
- Destination  
- Date/Time  
- Service type (bus, train, ferry, taxi, etc.)  
- Number of passengers  
- Provider filters (optional)

### FR-SEARCH-02  
The system shall return:

- List of available trips  
- Fare options  
- Seat/space availability  
- Trip duration & stops  
- Vehicle type (if available)  
- Provider branding

### FR-SEARCH-03  
Search must be tenant-aware and region-aware.

### FR-SEARCH-04  
Results must be sortable and filterable by:

- Price  
- Departure time  
- Provider  
- Rating (future)  
- Class/Seat type  

---

# 3.2 Fare & Pricing Engine

### FR-FARE-01  
The Fare Engine shall compute total cost based on:

- Provider base fare  
- Distance or zone  
- Dynamic pricing (optional)  
- Time-based pricing: peak/off-peak  
- Taxes  
- Tenant commission rules

### FR-FARE-02  
Fare rules must support per-tenant configuration.

### FR-FARE-03  
Additional charges must be supported:

- Luggage  
- Priority boarding  
- Service fees  
- VAT/GST

### FR-FARE-04  
Coupons, promo codes, and loyalty points may be supported later.

---

# 3.3 Reservation (Temporary Hold)

### FR-HOLD-01  
The system shall allow passengers to place a **reservation hold** on seats or capacity.

### FR-HOLD-02  
A reservation hold shall:

- Lock inventory temporarily  
- Prevent double booking  
- Expire automatically (default: 5–10 minutes)

### FR-HOLD-03  
Reservation holds shall be stored in Redis for speed.

### FR-HOLD-04  
Multiple passengers, seats, or segments must be supported.

### FR-HOLD-05  
Hold creation returns a `reservation_token` that must be used for booking completion.

---

# 3.4 Booking Confirmation & Payment

### FR-BOOK-01  
Bookings shall only be confirmed after successful payment.

### FR-BOOK-02  
System shall integrate with multiple payment providers (via adapters).

### FR-BOOK-03  
Booking workflow:

1. User searches  
2. User selects trip  
3. System fetches final price  
4. User confirms passenger details  
5. System creates reservation hold  
6. User initiates payment  
7. Payment provider returns success/failure  
8. System confirms booking and releases or converts hold  
9. Ticket is generated  
10. Notifications sent

### FR-BOOK-04  
If payment fails:

- Hold remains for remaining time OR  
- Is released immediately (configurable per tenant)

### FR-BOOK-05  
Booking confirmation generates:

- Booking reference (PNR)  
- Ticket ID  
- QR/Barcode  
- Payment receipt (optional)

---

# 3.5 Booking Modification

### FR-MOD-01  
Passengers may modify bookings depending on provider policy:

- Change date  
- Change time  
- Change passenger details  
- Change seat type  

### FR-MOD-02  
Modification fees or fare differences must be applied.

### FR-MOD-03  
Modification must re-check availability.

---

# 3.6 Cancellations & Refunds

### FR-CAN-01  
System shall support cancellation before departure, subject to provider rules.

### FR-CAN-02  
Refunds may be:

- Full  
- Partial  
- Non-refundable  

### FR-CAN-03  
Refund logic must support:

- Payment gateway refunds  
- Wallet/credit refunds (future)  
- Provider reconciliation

### FR-CAN-04  
Cancellation generates:

- Cancellation reference  
- Updated ticket status  
- Notification to provider & passenger

---

# 3.7 Ticket Generation & Validation

### FR-TICKET-01  
Tickets shall be generated automatically after booking confirmation.

### FR-TICKET-02  
Ticket content includes:

- Provider name  
- Trip info  
- Passenger names  
- Seat numbers  
- QR/Barcode  
- Validity rules  
- Terms and conditions

### FR-TICKET-03  
Tickets shall support multiple formats:

- PDF  
- QR only  
- Digital pass  
- Apple/Google wallet (future)

### FR-TICKET-04  
Tickets may be branded per tenant.

### FR-TICKET-05  
Ticket verification APIs shall be provided for:

- Providers  
- Inspectors  
- Validators  
- Terminals  
- Mobile scanning apps  

---

# 3.8 Provider Sync Engine

### FR-PROV-01  
Bookings must be synced to provider systems in real-time or near-real-time.

### FR-PROV-02  
Provider integration strategies:

- API push  
- API pull  
- Batch sync  
- Webhooks  
- Manual download (fallback)

### FR-PROV-03  
Provider sync errors must be logged and retried.

### FR-PROV-04  
Provider cancellation and modifications must be reconciled.

---

# 3.9 Multi-Leg & Multi-Modal Bookings (Future Capability)

The system must be architected to support:

- Multi-leg bookings (Train → Bus → Ferry)  
- Multi-provider journeys  
- Combined pricing  
- Combined ticketing  

Not required in MVP but must not block future roadmap.

---

## 4. Non-Functional Requirements

### 4.1 Performance

**NFR-PERF-01**  
Search queries must return within 300–500ms under load.

**NFR-PERF-02**  
Booking operations must remain under 500ms average.

**NFR-PERF-03**  
The system must be horizontally scalable.

### 4.2 Scalability

**NFR-SCALE-01**  
The Booking Engine must support:

- Multi-region deployments  
- Sharded availability data  
- Distributed reservation locks  
- Event queues or CQRS (future)

### NFR-SCALE-02  
The long-term scalability target is:

> **300 million concurrent/simultaneous booking-related transactions across regions**

This requires:

- Region-based traffic routing  
- Distributed Redis cluster  
- Partitioned bookings database  
- Multi-region PostgreSQL  
- Autoscaling load balancers  
- Provider-based partitioning  

### 4.3 Reliability

**NFR-REL-01**  
Booking engine must be fault-tolerant for:

- Payment failures  
- Sync failures  
- Cache node failures  
- Network latency

**NFR-REL-02**  
No confirmed booking should be lost.

### 4.4 Security

- All booking operations must require secure authentication.  
- Sensitive data encrypted at rest.  
- PCI/DSS compliance for payments (future).

---

## 5. Data Requirements (High-Level)

### Key Entities:

- Trip  
- Trip Segment  
- Fare Rule  
- Seat Inventory  
- Passenger  
- Booking  
- Booking Item/Segment  
- Ticket  
- Payment Transaction  
- Provider Sync Log  
- Cancellation/Modification Entry

Full ERD will be in:

📄 `docs/architecture/data-models/booking-data-model.md`  
(To be generated later)

---

## 6. Assumptions

- Providers supply updated seat inventories.  
- Network latency varies by region.  
- Payment providers define final success/failure.  
- Redis cluster available and scalable.

---

## 7. Future Enhancements

- Group bookings  
- Corporate billing  
- Offline validation  
- Loyalty points  
- AI pricing engine  
- Dynamic bundling of trips  
- Auto seat assignment  
- Automated rebooking in case of disruptions

---

## 8. Conclusion

The Booking & Ticketing Engine is the **heart** of Geo-Connect.  
It handles high-throughput, multi-provider, multi-region reservations, bookings, tickets, and cancellations.

This SRS will guide API design, database modeling, QA testing, and integration workflows for the booking lifecycle.
