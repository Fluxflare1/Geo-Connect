# Geo-Connect – Trip Planning & Routing SRS

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) defines the **Trip Planning & Routing Module** of the Geo-Connect MaaS platform.  
It describes how the system generates routes, retrieves schedules, interprets service provider data, and provides optimal trip recommendations to passengers.

The Trip Planning Module powers:

- Trip search  
- Route recommendations  
- Multi-modal journey structuring  
- Real-time service information  
- Provider schedule ingestion  
- Map-based navigation and distance calculations  

### 1.2 Scope

The module covers:

- Trip/route discovery  
- Schedule interpretation  
- Distance and duration calculation  
- Multi-segment routing  
- Multi-provider/multi-modal support  
- Real-time updates (future phase)  
- Map-based route generation  
- Operational region support per tenant  

### 1.3 Definitions

**Trip Plan:** A recommended path from origin to destination.  
**Segment:** A leg of a journey operated by a provider.  
**Mode:** Transportation type (bus, rail, taxi, ferry, shuttle, etc.).  
**Static Schedule:** Predefined service times.  
**Real-Time Feed:** Live updates (delay, disruption).  
**GTFS/GTFS-RT:** Common formats for transit schedules.  
**Headway:** Time between services.  
**Stop/Station:** A pickup or drop-off point.  
**Operational Zone:** Region a provider operates in.

---

## 2. System Overview

The Trip Planning module is composed of:

### 2.1 Static Data Engine
- Imports schedules from different providers.  
- Supports GTFS, CSV, API-based schedules, or custom formats.  
- Validates schedule consistency.

### 2.2 Route Generation Engine
- Computes optimal routes based on:
  - Time  
  - Distance  
  - Transfers  
  - Provider rules  
  - Passenger preferences  

### 2.3 Multi-Modal Engine
- Combines multiple modes (e.g., Bus → Rail → Taxi).  
- Handles segmentation, pricing aggregation, and time alignment.

### 2.4 Real-Time Engine (Future)
- Processes live data:
  - Arrival time  
  - Delays  
  - Disruptions  
  - Vehicle tracking (optional)  

### 2.5 Provider Integration Layer
- Syncs provider-specific routing data  
- Normalizes heterogeneous formats  
- Manages region-specific routing rules

---

## 3. Functional Requirements

---

# 3.1 Service Provider Data Ingestion

### FR-PROV-01  
The system shall allow providers to upload or sync route and schedule data.

### FR-PROV-02  
Supported formats include:

- GTFS  
- CSV  
- JSON API  
- Proprietary API feeds  
- Manual entry (admin panel)

### FR-PROV-03  
Routes must include:

- Stops or stations  
- Timetables  
- Service codes  
- Provider ID  
- Mode information  
- Vehicle type  
- Frequency/headway (optional)

### FR-PROV-04  
System must validate schedule integrity:

- Stop sequence  
- Overlapping times  
- Missing stops  
- Broken segments  
- Date validity

---

# 3.2 Trip Search & Routing

### FR-ROUTE-01  
Passengers shall be able to search for trips using:

- Origin  
- Destination  
- Date/time  
- Passenger count  
- Preferred mode  
- Provider filters  

### FR-ROUTE-02  
The system shall compute routes using:

- Static schedule data  
- Map-based road/travel distance  
- Real-time adjustments (when available)

### FR-ROUTE-03  
Response shall include:

- Trip segments  
- Departure & arrival times  
- Walking distance (if applicable)  
- Mode for each segment  
- Provider branding  
- Estimated total duration  
- Fare estimate (integration with fare engine)

### FR-ROUTE-04  
Routes must support:

- One-way  
- Round-trip  
- Multi-leg  
- Multi-modal  
- Open-jaw (future capability)

---

# 3.3 Multi-Modal Routing

### FR-MM-01  
System shall support combining multiple modes in a single trip.

### FR-MM-02  
The routing engine shall generate optimal combinations based on:

- Travel time  
- Walking time  
- Transfer points  
- Provider rules  
- Pricing constraints

### FR-MM-03  
Future expansion shall include:

- Bike-sharing  
- Car-sharing  
- Micro-mobility  
- On-demand/taxi integrations  

---

# 3.4 Distance, ETA, and Duration Calculation

### FR-DIST-01  
Distance shall be calculated using map provider APIs.

### FR-DIST-02  
Duration & ETA shall be computed using:

- Static schedule  
- Map route time  
- Average speed  
- Real-time traffic (future)

### FR-DIST-03  
Map provider selection shall be tenant-configurable:

- Google Maps  
- Mapbox  
- OpenStreetMap  
- Any custom provider  

---

# 3.5 Real-Time Information (Future Phase)

### FR-RT-01  
System shall process real-time feeds when providers support them.

Supported data types:

- Delays  
- Cancellations  
- Short-turns  
- Vehicle positions  
- Platform changes  

### FR-RT-02  
Real-time updates shall override static schedules.

### FR-RT-03  
System shall show:

- Countdown to arrival  
- Vehicle live location (if available)  
- Revised ETA  
- Alerts/notifications  

---

# 3.6 Geospatial Features

### FR-GEO-01  
System shall store geospatial data for:

- Stops  
- Routes  
- Stations  
- Regions  
- Service boundaries

### FR-GEO-02  
Geospatial queries must include:

- Nearby stops  
- Search radius filters  
- Polygon-based provider zones  

### FR-GEO-03  
System shall support GIS data formats.

---

# 3.7 Tenant Isolation & Custom Rules

### FR-TEN-01  
Trip planning must be tenant-aware:

- Operational zones  
- Provider branding  
- Preferred modes  
- Region/timezone  
- Local regulatory rules

### FR-TEN-02  
Tenants may override global routing rules.

---

## 4. Non-Functional Requirements

### 4.1 Performance

**NFR-PERF-01**  
Trip search must return results within 300–700ms under load.

**NFR-PERF-02**  
Routing calculations shall be cached for repeated queries.

**NFR-PERF-03**  
Route generation algorithms must be optimized for high volume.

### 4.2 Scalability

**NFR-SCALE-01**  
Trip planning must scale horizontally and across regions.

**NFR-SCALE-02**  
Static schedule storage must support:

- Large datasets  
- Multiple providers  
- Multiple regions  
- Full GTFS feeds  

### 4.3 Reliability

**NFR-REL-01**  
Trip planning must degrade gracefully if external APIs fail.

**NFR-REL-02**  
Fallback routing logic (distance-based) must exist.

### 4.4 Accuracy

**NFR-ACC-01**  
 ETA and distance calculations must be as accurate as supported by the selected map provider.

**NFR-ACC-02**  
System must update routing predictions with real-time data when available.

---

## 5. Data Requirements

### Key Data Objects

- Route  
- Stop/Station  
- Trip  
- Segment  
- Schedule  
- Fare zone  
- Shape/Polyline  
- Provider zone  
- Region  
- Real-time event (future)

A full ERD will be created under:

📄 `docs/architecture/data-models/trip-planning-data-model.md`

---

## 6. Future Enhancements

- AI-powered optimal routing  
- Predictive delay modeling  
- Crowdsourced travel-time estimations  
- Demand-based route generation  
- Personalized recommended trips  
- On-demand (ride-hailing) routing integration  
- Multilingual routing instructions  

---

## 7. Conclusion

This SRS defines the foundation of the Trip Planning & Routing system for Geo-Connect.  
It ensures accurate, fast, multi-modal trip discovery that will serve passengers across diverse transport providers and regions.
