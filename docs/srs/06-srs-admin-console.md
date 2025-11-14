# Geo-Connect – Admin Console SRS

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) defines the **Admin Console** — the master control center for managing tenants, providers, users, configurations, integrations, logs, and platform-wide settings for the Geo-Connect MaaS platform.

The Admin Console is used exclusively by:

- **Platform Operators** (Super Admins)  
- **Tenant Administrators**  
- **Support Staff**  

It provides full visibility and control across the ecosystem.

### 1.2 Scope

The Admin Console enables:

- Tenant & provider lifecycle management  
- User & role management  
- Global platform configuration  
- Catalog management supervision  
- Booking oversight  
- Financial settlement oversight  
- API key management  
- System monitoring & logs  
- Data export & reporting  
- Regional routing and deployment management  

### 1.3 Definitions

**Tenant Admin:** Admin responsible for a tenant’s configuration.  
**Platform Operator:** Super admin managing the entire platform.  
**Provider:** Transport operator connected to the platform.  
**Integration Key:** API key or credential for external providers.  
**Dashboard:** High-level metrics view.  
**Ops Logs:** System events and audit logs.

---

## 2. System Overview

The Admin Console is built using:

- **Next.js** (frontend)  
- **Django Admin APIs** (backend)  
- **Role-based access**  
- **Per-tenant isolation for tenant admins**  
- **Full system visibility for platform operators**  

---

## 3. Functional Requirements

---

# 3.1 Authentication & Access Control

### FR-ADMIN-AUTH-01  
Admin Console requires secure authentication (admin roles only).

### FR-ADMIN-AUTH-02  
Role hierarchy includes:

- Platform Operator  
- Tenant Admin  
- Provider Admin  
- Support Staff  

### FR-ADMIN-AUTH-03  
RBAC must enforce granular permissions.

### FR-ADMIN-AUTH-04  
Admins may reset passwords for users in their tenant.

---

# 3.2 Dashboard & Analytics

### FR-DASH-01  
Dashboard for platform operators shall include:

- Total users  
- Total trips  
- Daily active users  
- Peak usage  
- Revenue summaries  
- Failed bookings  
- Provider performance metrics  
- Region load distribution  

### FR-DASH-02  
Dashboard for tenant admins includes:

- Booking volume  
- Revenue breakdown  
- Provider performance under the tenant  
- Active tickets  
- User activity  

### FR-DASH-03  
Charts and metrics must be filterable by:

- Date range  
- Provider  
- Region  
- Mode  
- Status  

---

# 3.3 Tenant Management

### FR-TEN-01  
Administrators may:

- Create tenants  
- Suspend tenants  
- Terminate tenants  
- Update tenant settings  
- Configure tenant domains  

### FR-TEN-02  
Tenant configuration includes:

- Branding  
- Preferred payment provider  
- Map provider keys  
- Notification providers  
- Regions/timezones  
- Legal information  

### FR-TEN-03  
Tenant admins cannot view or modify other tenants.

---

# 3.4 Provider Management

### FR-PROV-01  
Platform admins may:

- Create provider accounts  
- Approve provider onboarding  
- Configure integration settings  
- Assign providers to tenants  

### FR-PROV-02  
Integration settings include:

- API keys  
- Webhook URLs  
- Sync frequency  
- Mode-specific configurations  

### FR-PROV-03  
Admin dashboard shows provider sync health status.

---

# 3.5 User Management

### FR-USR-01  
Admins may:

- Create or invite users  
- Assign roles  
- Suspend users  
- View user activity logs  

### FR-USR-02  
Tenant admins may manage user accounts **within their tenant only**.

### FR-USR-03  
Platform Operators can access all users globally.

---

# 3.6 Booking Oversight

### FR-BOOK-ADMIN-01  
Admins may view platform-wide bookings.

### FR-BOOK-ADMIN-02  
Tenant admins may view only their tenant’s bookings.

### FR-BOOK-ADMIN-03  
Admin console shows:

- Booking lifecycle  
- Payment status  
- Ticket status  
- Provider sync logs  
- Audit history  

### FR-BOOK-ADMIN-04  
Admins may cancel bookings on behalf of users (permissions required).

---

# 3.7 Catalog & Schedule Supervision

### FR-CAT-ADMIN-01  
Admins shall view provider catalogs:

- Routes  
- Stops  
- Schedules  
- Fare rules  

### FR-CAT-ADMIN-02  
Admins may:

- Trigger catalog re-sync  
- Upload GTFS manually  
- Approve or reject catalog submissions  
- View catalog version history  

### FR-CAT-ADMIN-03  
System flags:

- Invalid data  
- Missing stops  
- Overlapping schedules  
- Broken routes  

---

# 3.8 Payment & Financial Management

### FR-PAY-ADMIN-01  
Admins may view:

- Transactions  
- Refunds  
- Settlements  
- Provider earnings  
- Commission breakdown  

### FR-PAY-ADMIN-02  
Settlements:

- Can be generated manually or automatically  
- May be exported for accounting systems  

### FR-PAY-ADMIN-03  
Support staff can approve refunds (permission-based).

---

# 3.9 System Configuration

### FR-CONFIG-01  
Platform Operators may configure global settings:

- Default currency  
- Global commission rules  
- Allowed payment providers  
- Supported map providers  
- Notification routing  
- Regional routing logic  

### FR-CONFIG-02  
Tenant Admins may configure tenant-scoped settings.

### FR-CONFIG-03  
Configuration changes must be logged.

---

# 3.10 Logs & Monitoring

### FR-LOGS-01  
Admin Console shall include:

- System logs  
- Provider sync logs  
- Webhook logs  
- Authentication logs  
- Error logs  

### FR-LOGS-02  
Logs shall support:

- Filtering  
- Export  
- Real-time view (future)  
- Pagination  

### FR-LOGS-03  
Critical errors must trigger alerts.

---

# 3.11 API Key & Integration Management

### FR-KEY-01  
System shall store keys securely (encrypted).

### FR-KEY-02  
Admins may:

- Create keys  
- Rotate keys  
- Revoke keys  
- Assign scopes  

### FR-KEY-03  
Key usage logs must be viewable.

---

# 3.12 Region & Deployment Management

### FR-REGION-01  
Platform Operators:

- Configure operational regions  
- Assign providers to regions  
- Route traffic per region  

### FR-REGION-02  
Admin console shall show region load and cluster health.

### FR-REGION-03  
Integration with cloud-based deployment manager (roadmap).

---

# 3.13 Support & Case Management

### FR-SUPPORT-01  
Admins may view customer support requests.

### FR-SUPPORT-02  
Support staff may respond to user tickets.

### FR-SUPPORT-03  
Support logs must be stored per tenant.

### FR-SUPPORT-04  
Admins shall categorize and escalate cases.

---

## 4. Non-Functional Requirements

### 4.1 Performance

**NFR-PERF-01**  
Admin pages must load within 500ms.

**NFR-PERF-02**  
Large tables must support server-side pagination.

### 4.2 Security

- Only authorized admin roles may access the console  
- All API communications over HTTPS  
- Audit trail for all admin actions  
- Rate limiting on key-sensitive operations  

### 4.3 Reliability

- Logs must survive failures  
- Key operations must be idempotent  
- Multi-region failover strategy for super admin actions  

### 4.4 Scalability

- Support hundreds of tenants  
- Thousands of providers  
- Millions of bookings  
- Billions of logs stored over time  

---

## 5. Data Requirements

Key Data Entities:

- Tenant  
- Provider  
- Admin User  
- Roles & Permissions  
- Catalog Version  
- Booking  
- Payment Transaction  
- Settlement  
- API Key  
- Audit Log  
- Support Ticket  

Detailed ERD will be created in:

📄 `docs/architecture/data-models/admin-data-model.md`

---

## 6. Future Enhancements

- Real-time dashboards  
- AI-based anomaly detection  
- Predictive demand analytics  
- Monitoring provider SLA compliance  
- Stress/load testing management UI  
- Multi-region orchestration manager  

---

## 7. Conclusion

The Admin Console provides full operational visibility and configuration management for Geo-Connect.  
It is the backbone for system governance, ensuring stability, configurability, compliance, and performance across all tenants and regions.
