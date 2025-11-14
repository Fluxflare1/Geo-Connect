# Geo-Connect – Notifications Module SRS

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) defines the **Notifications Module** for the Geo-Connect MaaS platform.

The module ensures that users, providers, and administrators receive timely and context-aware notifications via:

- Email  
- SMS  
- Push notifications (future)  
- In-app notifications  
- Webhooks  

It supports transactional alerts, updates, reminders, and system events.

### 1.2 Scope

The Notifications Module covers:

- Sending messages across channels (email, SMS, in-app, webhook)  
- Template management  
- Tenant-level notification configuration  
- Provider-level configuration  
- Event triggers and routing  
- Notification logs  
- Retry mechanisms  
- Multi-region routing  
- SMTP/SMS gateway integration  
- Webhook dispatch  

### 1.3 Definitions

**Notification Channel:** Email, SMS, in-app, webhook.  
**Event Trigger:** System action that initiates a message.  
**In-App Center:** Notification UI inside customer/provider apps.  
**Provider:** Transport operator integrated with Geo-Connect.  
**Tenant:** Client using the platform under their branding.

---

## 2. System Overview

Notifications module consists of:

### 2.1 Channels
- Email (via pluggable SMTP providers)  
- SMS (via configurable SMS gateways)  
- In-App (via DB + websockets long-term)  
- Webhooks (provider integrations)  
- Push (future: FCM/APNs)

### 2.2 Backend Component (Django)
- Event listener  
- Dispatch engine  
- Fallback routing  
- Template rendering  
- Retry scheduler  
- Notification logging  
- Multi-region queueing with Celery/Redis  

### 2.3 Frontend Component (Next.js)
- Notification center UI  
- Delivery status indicators  
- Tenant-specific branding  

---

## 3. Functional Requirements

---

# 3.1 Event Triggers

Notifications shall be triggered by:

### Booking Events
- Booking created  
- Booking confirmed  
- Booking failed  
- Booking cancelled  
- Booking expired  
- Ticket issued  

### Payment Events
- Payment successful  
- Payment failed  
- Refund processed  

### Trip Events
- Trip delayed  
- Trip cancelled  
- Boarding reminder  
- Trip started  
- Trip completed  

### Provider Events
- Provider onboarding approved  
- Provider integration errors  
- Sync failures  

### Tenant/Admin Events
- New admin invite  
- Password reset  
- API key rotation  
- SLA violation alerts  
- Settlement report ready  

---

# 3.2 Recipient Types

### FR-RECIP-01  
Notifications can be sent to:

- Passengers (customers)  
- Provider admins  
- Tenant admins  
- Platform operators  
- External systems via webhook  

### FR-RECIP-02  
Recipient lists must be dynamically generated based on rules.

---

# 3.3 Email Notifications

### FR-EMAIL-01  
System must support any SMTP provider via:

- Host  
- Port  
- Username  
- Password  
- TLS/SSL  

### FR-EMAIL-02  
Email templates must be tenant-customizable:

- Header/footer  
- Branding  
- Sender address  

### FR-EMAIL-03  
Email events include:

- Booking confirmation  
- Payment receipt  
- Ticket delivery  
- Support response  
- Admin alerts  

---

# 3.4 SMS Notifications

### FR-SMS-01  
System must support pluggable SMS providers such as:

- Twilio  
- Termii  
- Africa’s Talking  
- Nexmo  
- Any gateway via HTTP API  

### FR-SMS-02  
SMS delivery rules:

- Short templates  
- Fallback to email if SMS fails (configurable)  
- Region-based routing  

### FR-SMS-03  
SMS events include:

- OTP codes  
- Booking reminders  
- Payment confirmation  
- Trip updates  

---

# 3.5 In-App Notifications

### FR-INAPP-01  
In-app notifications stored in DB.

### FR-INAPP-02  
Users shall view notifications in customer/provider apps.

### FR-INAPP-03  
Notifications may include:

- Read/unread states  
- Timestamp  
- Metadata (booking ID, trip ID, etc.)  

### FR-INAPP-04  
Pagination required for large volumes.

---

# 3.6 Webhooks

### FR-WEBHOOK-01  
Webhook endpoints defined per provider/tenant.

### FR-WEBHOOK-02  
Webhook events include:

- Booking events  
- Ticket events  
- Payment events  
- Integration-status events  

### FR-WEBHOOK-03  
Webhook delivery characteristics:

- Retries with exponential backoff  
- Signed payloads  
- HTTPS-only  
- Delivery logs and timestamps  

---

# 3.7 Template Management

### FR-TEMPLATE-01  
Templates must support variables (e.g. {{booking_id}}, {{user_name}}).

### FR-TEMPLATE-02  
Admins may:

- View  
- Edit  
- Duplicate  
- Restore defaults  

### FR-TEMPLATE-03  
Templates are versioned.

---

# 3.8 Notification Routing

### FR-ROUTING-01  
Routing rules per tenant may define:

- Preferred SMS provider  
- Preferred email provider  
- Fallback channels  
- Time-of-day routing  
- Region-based routing  

### FR-ROUTING-02  
Routing rules must be editable via Admin Console.

### FR-ROUTING-03  
Notifications must be routed to nearest/available region.

---

# 3.9 Delivery Tracking & Logging

### FR-LOGS-01  
System shall store logs for:

- Sent notifications  
- Failures  
- Retries  
- Response payloads  
- Delivery timestamps  

### FR-LOGS-02  
Logs must be filterable by:

- Date  
- Channel  
- Event  
- Tenant  
- Provider  
- Status  

### FR-LOGS-03  
Logs stored long-term for auditing.

---

# 3.10 Retry Mechanisms

### FR-RETRY-01  
Failed deliveries must be retried automatically.

### FR-RETRY-02  
Retry levels:

- Level 1: immediate retry  
- Level 2: 1 min  
- Level 3: 5 mins  
- Level 4: 30 mins  
- Level 5: 2 hours  

### FR-RETRY-03  
Maximum retries configurable per event type.

---

# 3.11 Notification Preferences

### FR-PREF-01  
Users shall configure:

- Opt-in/opt-out categories  
- Email vs SMS preference  
- Quiet hours (future)  
- Language preference  

### FR-PREF-02  
Tenants may override some categories (regulatory).

---

# 3.12 High-Volume Delivery Handling

### FR-HIGHVOLUME-01  
System must handle **300 million concurrent notifications** across regions.

### FR-HIGHVOLUME-02  
Supports:

- Horizontal scaling with workers  
- Region-partitioned queues  
- Batched processing  

### FR-HIGHVOLUME-03  
Must support peak traffic scenarios such as:

- Festival schedules  
- Metro shutdowns  
- Sudden trip cancellations  
- Global incidents affecting mobility  

---

## 4. Non-Functional Requirements

### 4.1 Performance

- Notification generation < 100ms  
- Email/SMS gateway dispatch < 500ms  
- Webhook dispatch < 300ms  

### 4.2 Scalability

- Fully distributed  
- Multi-region worker clusters  
- Queue sharding  
- Stateless dispatch services  

### 4.3 Reliability

- Guaranteed delivery (with retries)  
- Durable logs  
- Failover for gateways  
- Region-isolated failures  

### 4.4 Security

- Encrypted secrets  
- Signed webhook payloads  
- Tamper-proof logs  
- RBAC-based template editing  

---

## 5. Data Requirements

Data stored:

- Notification ID  
- Channel  
- Payload  
- Status  
- Failure reason  
- Retry count  
- User/tenant/provider reference  
- Template version  
- Timestamp  

Detailed database model will exist in:

📄 `docs/architecture/data-models/notifications-data-model.md`

---

## 6. Future Enhancements

- Push notifications via FCM/APNs  
- AI-based routing optimization  
- Deliverability scoring  
- Adaptive retry engine  
- NLP-based message personalization  

---

## 7. Conclusion

The Notifications Module provides a resilient and scalable messaging infrastructure for Geo-Connect, ensuring timely delivery of booking updates, payment alerts, trip information, operational messages, and system events across all regions.
