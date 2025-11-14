# Geo-Connect – Trip Planning Module SRS

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) defines the **Trip Planning Module** for the Geo-Connect MaaS platform.

The module provides multi-modal trip discovery, route optimization, real-time travel updates, and intelligent recommendations to passengers across all supported transportation modes.

### 1.2 Scope

The Trip Planning module includes:

- Multi-modal route planning  
- Real-time route updates  
- Stop/station lookup  
- Transfer coordination  
- Fare estimation  
- Provider/vehicle availability  
- Service disruption integration  
- Map-based navigation  
- Regional routing logic  
- Caching & performance optimization  
- Predictive (future) capabilities  

### 1.3 Definitions

**Multi-Modal Trip:** A trip that may involve multiple modes (bus + ferry + train).  
**Static Data:** GTFS schedules, operating hours, stops, routes.  
**Real-Time Data:** Vehicle locations, delays, cancellations.  
**Route Engine:** Algorithm that generates optimal routes.  
**Headway:** Time between vehicles on a route.  
**Service Window:** Expected time range a trip can occur.

---

## 2. System Overview

Trip Planning operates on:

### 2.1 Frontend (Next.js)
- Search form  
- Map rendering  
- Trip results (list + map)  
- Itinerary details  

### 2.2 Backend (Django)
- Trip planning API  
- Real-time data ingestion  
- Multi-modal routing engine  
- Region-specific routing logic  
- Caching layer  
- Error/fallback handling  

### 2.3 Data Sources
- Provider static schedules (GTFS, API, CSV)  
- Provider real-time feeds (GTFS-RT, internal APIs)  
- Map services (Google Maps, OpenStreetMap, Mapbox, HERE, or tenant-specific)  
- Geo-Connect Catalog Service  
- Traffic/incident data (optional)  

---

## 3. Functional Requirements

---

# 3.1 Trip Search

### FR-TRIP-SEARCH-01  
Users can search for trips using:

- Origin  
- Destination  
- Departure time  
- Arrival time  
- Travel date  
- Mode filters (bus, ferry, rail, ride-hailing, etc.)  
- Provider filters  

### FR-TRIP-SEARCH-02  
The system shall validate:

- Coordinates  
- Service availability  
- Time windows  

### FR-TRIP-SEARCH-03  
Queries must support:

- Exact text search  
- Autocomplete search  
- Map pin search  
- Saved locations  

---

# 3.2 Multi-Modal Routing Options

### FR-MULTI-01  
Routing engine must support:

- Single mode  
- Mixed modes (bus → train → shuttle)  
- Walking & last-mile legs  
- Ride-hailing as optional first/last segment  

### FR-MULTI-02  
Generated itineraries must include:

- Total travel time  
- Walking time  
- Transfer counts  
- Fare estimates  
- Real-time adjustments (if available)  

---

# 3.3 Itinerary Ranking & Optimization

### FR-RANK-01  
Itineraries must be ranked by:

- Fastest  
- Cheapest  
- Most convenient (fewest transfers)  
- Preferred mode (user setting)

### FR-RANK-02  
Future ML ranking engine may apply:

- Historical reliability  
- User preference patterns  
- Provider performance metrics  

---

# 3.4 Fare Estimation

### FR-FARE-01  
Trip planning must estimate fares using:

- Provider fare rules  
- Distance-based calculations  
- Zones  
- Time-based pricing  
- Transfer discounts (if supported)  
- Multi-leg fare aggregation  

### FR-FARE-02  
Fare estimates displayed with:

- Base fare  
- Surcharges  
- Taxes  
- Total  

---

# 3.5 Real-Time Updates

### FR-REALTIME-01  
Engine must incorporate real-time updates:

- Arrival/departure delays  
- Service disruptions  
- Early closures  
- Route diversions  
- Cancelled trips  

### FR-REALTIME-02  
When real-time impacts a route:

- Update itinerary  
- Notify user (if subscribed)  
- Provide alternatives  

---

# 3.6 Map & Navigation

### FR-MAP-01  
Using configurable providers (tenant-specific), system must display:

- Routes  
- Stops  
- Walking paths  
- Vehicles (if available)  
- Estimated arrival times  

### FR-MAP-02  
User may switch between:

- Map view  
- List view  

### FR-MAP-03  
Integrated geocoder must provide:

- Reverse geocoding  
- Address suggestions  
- Landmark search  

---

# 3.7 Stop & Route Information

### FR-STOPS-01  
Users may view:

- All stops  
- Stop schedules  
- Stop amenities (optional)  
- Real-time arrivals  

### FR-STOPS-02  
Route info must include:

- Stops list  
- Operator info  
- timetables  
- Real-time updates  

---

# 3.8 Offline & Fallback Behavior

### FR-OFFLINE-01  
System must handle degraded map service by:

- Showing cached stop data  
- Showing cached routes  
- Fallback itinerary generation  

### FR-OFFLINE-02  
In case of provider API failure:

- Use last known static data  
- Mark real-time status as unavailable  

---

# 3.9 Transfer Management

### FR-TRANS-01  
Routing engine must ensure:

- Minimum transfer time  
- Walking distance estimation  
- Same-station transfers  
- Cross-terminal transfers  

### FR-TRANS-02  
Transfer legs must show:

- Walk time  
- Estimated transfer safety margin  
- Alerts if tight  

---

# 3.10 Advanced Filters

### FR-FILTER-01  
Filters include:

- Lowest price  
- Fastest  
- Limited transfers  
- Wheelchair accessible  
- Bikes allowed  
- Air conditioning  
- Provider-specific features  

---

# 3.11 API Access for Providers

### FR-API-01  
Providers may supply:

- Real-time feeds  
- Static data  
- Schedule changes  
- Route closures  

### FR-API-02  
Webhook-based push updates supported.

---

## 4. Non-Functional Requirements

### 4.1 Performance

- Query response target: 300–600ms  
- Pre-computed cached itineraries available  
- Real-time updates: <150ms ingestion  

### 4.2 Scalability

- Must support billions of route calculations per day  
- Region-partitioned routing clusters  
- Load-balanced API  
- Multi-region failover  

### 4.3 Reliability

- Route engine must degrade gracefully  
- Cached fallbacks remain valid for 30–60 minutes  
- Redundant map providers supported  

### 4.4 Security

- Provider APIs authenticated  
- Map provider keys secured per tenant  
- Rate limiting per user/IP  

---

## 5. Data Requirements

Trip planning depends on:

- Static route data  
- Stop data  
- Timetables  
- Provider metadata  
- Real-time updates  
- Region topology  
- Fare rules  

Data model will be documented in:

📄 `docs/architecture/data-models/trip-planning-data-model.md`

---

## 6. Future Enhancements

- ML-based dynamic routing  
- Demand prediction  
- Crowd density forecasting  
- Personalized route recommendations  
- Carbon footprint scoring  
- Micro-mobility (e-bikes, scooters) integration  

---

## 7. Conclusion

The Trip Planning Module provides the intelligence behind Geo-Connect’s mobility experience.  
It enables multi-modal routing, real-time updates, fare estimation, transfer coordination, and flexible integration with providers and map sources.
