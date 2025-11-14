# Geo-Connect – Analytics & Reporting SRS

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) defines the **Analytics & Reporting Module** for the Geo-Connect MaaS platform.  
It covers all analytical processes, dashboards, KPIs, insights, forecasting, data pipelines, aggregation routines, and reporting tools used by:

- Platform Operators  
- Tenant Admins  
- Provider Admins  
- Business Analysts  
- Finance Teams  

### 1.2 Scope

The module provides:

- Real-time dashboards  
- Batch analytics pipelines  
- Operational KPIs  
- Revenue analytics  
- Trip and booking insights  
- Load monitoring  
- Region-level performance insights  
- Provider ranking and SLA monitoring  
- Exportable reports  
- Data lake storage (future)  
- Predictive analytics (future)  

### 1.3 Definitions

**KPI:** Key performance indicator.  
**Aggregation Pipeline:** Processing logic that summarizes raw data.  
**SLA:** Service-level agreement with providers.  
**ETL/ELT:** Data extraction and transformation tools.  
**Data Lake:** Low-cost storage for raw data.

---

## 2. System Overview

Analytics & Reporting consist of:

### 2.1 Frontend (Next.js)
- UI dashboards  
- Charts (area, bar, pie, time-series)  
- Filters and export buttons  

### 2.2 Backend (Django)
- Analytics API  
- ETL/processing jobs  
- Scheduled summarization  
- Cached metrics  

### 2.3 Data Sources
- Bookings service  
- Ticketing service  
- Provider service  
- Trip planning service  
- Settlements & payments  
- Notifications  
- Logs and events  

### 2.4 Storage
- PostgreSQL (OLTP)  
- Analytical tables (OLAP aggregated tables)  
- Redis/Cache layer  
- (Future) Data lake or BigQuery/Snowflake  

---

## 3. Functional Requirements

---

# 3.1 Real-Time Dashboards

### FR-RT-01  
System shall provide real-time metrics including:

- Active users  
- Live bookings being processed  
- System load per region  
- Provider API health  
- Payment gateway health  
- Success vs failure booking ratio  

### FR-RT-02  
Updates frequency configurable (default: 5–10 seconds).

---

# 3.2 Booking Analytics

### FR-BOOK-AN-01  
Admins shall view:

- Total bookings  
- Successful bookings  
- Failed bookings  
- Cancelled bookings  
- Abandoned (incomplete) bookings  

### FR-BOOK-AN-02  
Booking metrics must support filtering by:

- Date range  
- Mode (bus, taxi, ferry, train, ride-hailing…)  
- Provider  
- Tenant  
- Region  

### FR-BOOK-AN-03  
System shall calculate:

- Booking conversion rate  
- Average reservation hold duration  
- Payment success ratio  
- Booking lead time  

---

# 3.3 Revenue & Financial Analytics

### FR-REV-01  
Admins shall view:

- Total revenue  
- Revenue by provider  
- Revenue by mode  
- Revenue by tenant  
- Commission earnings  
- Daily/weekly/monthly revenue charts  

### FR-REV-02  
Pricing insights:

- Average ticket price  
- Price distribution  
- Revenue per passenger  

### FR-REV-03  
Finance teams may export:

- Commission reports  
- Provider settlement reports  
- Refund logs  
- Transaction summaries  

---

# 3.4 Provider Performance & SLA

### FR-PROVIDER-SLA-01  
System shall track:

- Provider response time  
- API uptime  
- Sync success/failure  
- Ride/trip cancellation rate  
- Delayed trips  
- Capacity utilization  

### FR-PROVIDER-SLA-02  
SLA violations shall trigger alerts.

### FR-PROVIDER-SLA-03  
Providers may access their own performance dashboard.

---

# 3.5 Region & Network Analytics

### FR-REGION-01  
System shall show per-region:

- Demand (searches & bookings)  
- Peak hour load  
- Popular routes  
- Network congestion  
- Success vs failure rates  
- Payment gateway behaviour  
- Provider availability  

### FR-REGION-02  
Admin console must support:

- Heatmaps  
- Time-based performance charts  
- Route utilization graphs  

---

# 3.6 Customer Insights & Behaviour

### FR-CUSTOMER-01  
System shall display:

- New vs repeat users  
- User retention  
- Device/platform usage  
- Funnel analytics (search → select → pay → ticket)  

### FR-CUSTOMER-02  
User segmentation:

- Heavy users  
- Occasional users  
- Low-value users  
- High-value users  

### FR-CUSTOMER-03  
Future integrations:

- Recommendations  
- Personalization  
- Targeted notifications  

---

# 3.7 Operational Reporting

### FR-OP-01  
Platform operators may generate:

- Daily operational summaries  
- Provider health reports  
- Incident reports  
- System performance logs  

### FR-OP-02  
Reports may be:

- Viewed in dashboard  
- Exported as CSV  
- Delivered by email (scheduled)  

---

# 3.8 Scheduled Reports & Automation

### FR-SCHED-01  
Admins may schedule:

- Daily  
- Weekly  
- Monthly  

Reports.

### FR-SCHED-02  
Scheduling supports:

- Email delivery  
- Provider-specific scheduling  
- Custom date ranges  

### FR-SCHED-03  
Job failures must be logged and notified.

---

# 3.9 ETL / Data Processing Pipelines

### FR-ETL-01  
The system shall support:

- Incremental data ingestion  
- Aggregation windows: hourly, daily, weekly  
- Rebuild pipelines (for corrections)  

### FR-ETL-02  
Transformations include:

- Summaries  
- De-duplication  
- Normalization  
- Partitioning by region/provider/date  

### FR-ETL-03  
Large ETL jobs must run asynchronously.

---

# 3.10 Exports & Integrations

### FR-EXPORT-01  
Admins may export:

- Booking data  
- Revenue data  
- Logs  
- Provider performance  
- Customer segmentation  

### FR-EXPORT-02  
Supported formats:

- CSV  
- JSON  

### FR-EXPORT-03  
Exports must support pagination and chunking for very large datasets.

---

## 4. Non-Functional Requirements

### 4.1 Performance

**NFR-PERF-01**  
Aggregated KPI queries should respond within 200–500ms.

**NFR-PERF-02**  
Large data exports must not block UI.

### 4.2 Scalability

- Must support **300M+ transactions**  
- Partitioned analytical tables  
- Region-based clustering  
- Sharded datasets  

### 4.3 Reliability

- ETL jobs must retry on failure  
- Audit logs stored permanently  
- Export history preserved  

### 4.4 Security

- Analytics endpoints read-only  
- Role-based visualization  
- Sensitive data masked  
- Export logs recorded  

---

## 5. Data Requirements

Key dataset categories:

- Raw: Bookings, tickets, payments, logs  
- Aggregated: Daily/weekly/monthly summaries  
- Derived: KPIs, trends, forecasts  

Data models will be documented in:

📄 `docs/architecture/data-models/analytics-data-model.md`

---

## 6. Future Enhancements

- Predictive analytics & forecasting  
- ML anomaly detection  
- Customer lifetime value (CLV)  
- Provider recommendation engine  
- Mobility demand prediction  
- AI-powered revenue optimization  

---

## 7. Conclusion

The Analytics & Reporting module provides the intelligence layer of Geo-Connect.  
It supports decision-making, operational monitoring, financial oversight, and predictive capacity for tenants, providers, and the platform operator.
