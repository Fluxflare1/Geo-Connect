# Geo-Connect – Pricing & Fares Module SRS

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) defines the **Pricing & Fares Module** of the Geo-Connect MaaS platform.

This module determines how fares are calculated, managed, configured, and delivered to:

- Passengers  
- Providers  
- Tenants  
- Booking & Trip Planning engines  
- Analytics & Reporting systems  

### 1.2 Scope

This module covers:

- Fare rules  
- Dynamic pricing  
- Zones & distance-based pricing  
- Multi-leg fare aggregation  
- Transfer fares  
- Peak/off-peak pricing  
- Provider pricing configuration  
- Promotions (future)  
- API integration  
- Fare pre-computation & caching  
- Pricing overrides  

### 1.3 Definitions

**Fare Rule:** A rule determining how price is computed.  
**Zone Pricing:** Fare based on geographic zones.  
**Dynamic Pricing:** Price varies based on demand/time.  
**Multi-Leg Fare:** Combined price for multi-modal itineraries.  
**Transfer Fare:** Discount or surcharge for switching modes/vehicles.  
**Provider:** Transportation operator.  
**Tenant:** Client using the platform.

---

## 2. System Overview

The Pricing & Fares module interacts with:

### 2.1 Trip Planning Engine
- Generates estimated fares for itineraries.  
- Consumes fare rules as input.

### 2.2 Booking Engine
- Applies final fare calculation.  
- Handles taxes, surcharges, and promo codes.

### 2.3 Provider Service
- Stores pricing configuration per provider.

### 2.4 Admin Console
- UI for configuring fare rules.  

### 2.5 Customer App
- Displays fare breakdown to passengers.

### 2.6 Analytics Service
- Uses pricing data for revenue estimates.

---

## 3. Functional Requirements

---

# 3.1 Fare Rule Management

### FR-FARE-01  
System must support these pricing models:

- Flat fare  
- Distance-based  
- Time-based  
- Zone-based  
- Seat-class-based  
- Provider-custom pricing  
- Dynamic demand pricing  
- Multi-leg aggregation  

### FR-FARE-02  
Administrators may:

- Create  
- Edit  
- Version  
- Activate/deactivate  

fare rules.

### FR-FARE-03  
Fare rules are tenant- and provider-specific.

---

# 3.2 Fare Calculation

### FR-CALC-01  
Given an itinerary, system must compute:

- Base fare  
- Additional surcharges  
- Taxes  
- Transfer rules  
- Provider-specific adjustments  

### FR-CALC-02  
Fare calculation must occur:

- During trip planning (estimate)  
- During booking (final)  

### FR-CALC-03  
Fare engine must support caching for repeated calculations.

---

# 3.3 Zone-Based Pricing

### FR-ZONE-01  
Zones may be:

- Circular  
- Polygon  
- Provider-defined  
- Multi-region  

### FR-ZONE-02  
Pricing between zones may include:

- Flat price  
- Tiered pricing  
- Discounted transfers  

---

# 3.4 Distance-Based Pricing

### FR-DIST-01  
Distance calculated using:

- Map provider geometry  
- Provider GTFS route distances  
- Geo-Connect routing engine  

### FR-DIST-02  
Pricing may include:

- Per-km base  
- Minimum fare  
- Maximum fare  

---

# 3.5 Time-Based Pricing

### FR-TIME-01  
System must support:

- Time-of-day fares  
- Peak vs off-peak  
- Weekend vs weekday  
- Public holiday adjustments  

### FR-TIME-02  
Dynamic calculations consider:

- Congestion  
- Demand  
- Weather (future)  
- Provider capacity  

---

# 3.6 Multi-Leg Fares

### FR-MULTI-LEG-01  
System must support:

- Joint fares across providers  
- Single-ticket transfers  
- Fare caps for daily/weekly passes  

### FR-MULTI-LEG-02  
Transfers can include:

- Discount  
- Zero-charge  
- Premium fee  

based on provider rules.

---

# 3.7 Provider-Specific Rules

### FR-PROV-FARE-01  
Provider admins may configure:

- Base fares  
- Taxes  
- Surcharges  
- Discounts  
- Minimum & maximum limits  

### FR-PROV-FARE-02  
Providers may override tenant defaults.

### FR-PROV-FARE-03  
Provider fare versions must be logged.

---

# 3.8 Dynamic Pricing

### FR-DYN-01  
Dynamic pricing may consider:

- Demand  
- Supply  
- Weather  
- Traffic  
- Historical patterns  
- Provider load  

### FR-DYN-02  
Dynamic pricing must be:

- Real-time  
- Cached  
- Can be disabled by tenant  

### FR-DYN-03  
Dynamic multipliers may apply:

- Surge  
- Discount  
- Event-based pricing  

---

# 3.9 Taxes & Surcharges

### FR-TAX-01  
System must support:

- VAT  
- Provider-specific taxes  
- Government levies  
- Service fees  

### FR-TAX-02  
Surcharges may include:

- Night service  
- Airport fee  
- Premium seat fee  
- Holiday surcharge  

---

# 3.10 Promotions & Discounts (Future)

### FR-PROMO-01  
Promo engine will support:

- Coupons  
- Auto-applied rules  
- Loyalty points  
- Membership tiers  

### FR-PROMO-02  
Promotions configurable by tenant.

---

# 3.11 Fare Transparency

### FR-TRANSP-01  
Passenger-facing UI must show:

- Base fare  
- Taxes  
- Surcharges  
- Discounts  
- Total payable amount  

### FR-TRANSP-02  
Trip planning must show **estimated** fare.

### FR-TRANSP-03  
Booking must show **final fare** before payment.

---

# 3.12 Audit & History

### FR-AUDIT-01  
Fare rule changes must be versioned.

### FR-AUDIT-02  
Fare calculations must be audit logged.

### FR-AUDIT-03  
Historical fares must remain usable for bookings made earlier.

---

## 4. Non-Functional Requirements

### 4.1 Performance

- Fare calculation < 150ms  
- Batch fare update jobs < 1 minute  
- Dynamic pricing refresh < 10 seconds  

### 4.2 Scalability

- Able to compute fares for millions of trips per hour  
- Region-aware pricing services  
- Horizontal scaling of fare engine  

### 4.3 Reliability

- Fare computation must always produce a value  
- Fallback rules triggered if primary rules unavailable  
- Versioning ensures reproducibility  

### 4.4 Security

- Provider keys encrypted  
- Tamper-proof pricing logs  
- RBAC-controlled rule editing  

---

## 5. Data Requirements

Pricing module stores:

- Fare rules  
- Zone definitions  
- Pricing versions  
- Surcharges  
- Taxes  
- Dynamic pricing multipliers  
- Audit logs  

Data model documented in:

📄 `docs/architecture/data-models/pricing-fares-data-model.md`

---

## 6. Future Enhancements

- ML-based price prediction  
- Real-time seat-level pricing  
- Competitor fare comparison  
- Fare optimization engine  
- Passenger-specific dynamic pricing  

---

## 7. Conclusion

The Pricing & Fares module provides a flexible, scalable, region-aware and provider-driven pricing system for Geo-Connect.  
It supports simple, complex, static, and dynamic fare models, powering the booking and trip planning engines with accurate and transparent fare calculations.
