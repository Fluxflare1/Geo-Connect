# Geo-Connect – Customer Experience SRS

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) defines the **Customer Experience (CX) Module** for the Geo-Connect MaaS platform.  
It describes all user-facing functionality for passengers, including registration, trip search, booking flows, payment, ticket viewing, account management, notifications, and customer support.

### 1.2 Scope

This module covers:

- Passenger registration & login  
- Profile management  
- Search & trip discovery  
- Booking and payment workflows  
- Ticket display  
- Booking history  
- Notifications  
- Customer support  
- Device responsiveness (mobile-first)  
- Multi-language and accessibility (roadmap)  

### 1.3 Definitions

**Passenger:** End-user booking transportation services.  
**Customer Interface:** Web or mobile frontend used by passengers.  
**CX:** Customer Experience.  
**Booking History:** List of past and active bookings.  
**Ticket Wallet:** Interface showing stored tickets.  
**Notification Center:** In-app view for updates.

---

## 2. System Overview

Customer Experience consists of:

### 2.1 Web App (Next.js + Tailwind + shadcn-ui)
- Responsive UI  
- Branding support per tenant  
- public-facing interface available at tenant domain  

### 2.2 Customer Authentication
- Login  
- Passwordless login (optional)  
- Social login (future)  
- JWT/session-based  

### 2.3 Trip Search & Planning
- Search form  
- Multi-modal trip search results  
- Sorting & filtering  

### 2.4 Booking & Ticket Wallet
- Booking checkout  
- Payment integration  
- Ticket generation  
- Ticket display with QR code  

### 2.5 Customer Profile
- Personal info  
- Saved preferences  
- Saved routes (future)  

### 2.6 Notification Center
- In-app notifications  
- Email/SMS integration  
- Real-time updates (future)

### 2.7 Customer Support
- Help center  
- Contact support form  
- FAQ  
- Chatbot or live chat integration (future)

---

## 3. Functional Requirements

---

# 3.1 Authentication & Registration

### FR-AUTH-01  
Passengers shall be able to:

- Register  
- Login  
- Logout  
- Reset password  

### FR-AUTH-02  
Authentication methods:

- Email + password  
- OTP (optional configuration)  
- Social login (future)  

### FR-AUTH-03  
Each tenant may configure authentication rules.

### FR-AUTH-04  
User sessions must follow secure token standards.

---

# 3.2 Customer Profile Management

### FR-PROFILE-01  
Passengers shall view and update:

- Name  
- Email  
- Phone  
- Preferred language  
- Emergency contact (optional)  

### FR-PROFILE-02  
Passengers shall upload a profile picture (optional).

### FR-PROFILE-03  
Passengers may view:

- Payment methods (tokenized)  
- Saved tickets  
- Saved preferences  

---

# 3.3 Trip Search & Discovery

### FR-SEARCH-01  
Users can search by:

- Origin  
- Destination  
- Date/time  
- Mode  
- Provider filter  

### FR-SEARCH-02  
Search results shall show:

- Estimated fares  
- Duration  
- Transfers  
- Provider branding  
- Seat availability (if applicable)

### FR-SEARCH-03  
Search results may be sorted by:

- Lowest price  
- Fastest trip  
- Earliest departure  

### FR-SEARCH-04  
Search shall use map services configured per tenant.

---

# 3.4 Booking & Payment Flow

### FR-BOOK-01  
The booking workflow shall include:

1. Select trip  
2. View fare breakdown  
3. Input passenger details  
4. Select seat (if required)  
5. Apply promo code (future)  
6. Confirm reservation  
7. Redirect to payment  
8. Booking success  
9. Ticket generated  

### FR-BOOK-02  
System shall warn users before reservation hold expires.

### FR-BOOK-03  
If payment fails:

- Retry option  
- Return to booking page  
- Hold may be extended (tenant rule)

---

# 3.5 Ticket Wallet

### FR-TICKET-01  
Customers shall access all active and past tickets.

### FR-TICKET-02  
Tickets shall display:

- QR/Barcode  
- Trip details  
- Passenger info  
- Seat number  
- Provider branding  

### FR-TICKET-03  
Tickets shall be accessible offline (cached mode future).

---

# 3.6 Booking History

### FR-HISTORY-01  
Passengers shall view all bookings:

- Upcoming  
- Completed  
- Cancelled  
- Expired  

### FR-HISTORY-02  
History shall support filters for:

- Date range  
- Provider  
- Status  
- Mode  

---

# 3.7 Notifications & Alerts

### FR-NOTIF-01  
System shall display notifications for:

- Booking confirmation  
- Payment failure  
- Trip delay or cancellation  
- Promo messages (tenant feature)  

### FR-NOTIF-02  
Notifications to be delivered via:

- Email  
- SMS  
- In-app center  

### FR-NOTIF-03  
Notification settings configurable per user.

---

# 3.8 Multi-Language Support

### FR-INTL-01  
System architecture must support localization strings.

### FR-INTL-02  
Default languages:

- English  
(Additional languages future)

---

# 3.9 Customer Support

### FR-SUPPORT-01  
Passengers shall access a help center.

### FR-SUPPORT-02  
Support channels:

- Contact form  
- FAQ  
- Email  
- Telephone (if provided by tenant)  

### FR-SUPPORT-03  
Support requests shall be logged with:

- Category  
- Priority  
- User  
- Tenant  
- Timestamp  

---

## 4. Non-Functional Requirements

---

### 4.1 Performance

**NFR-PERF-01**  
Page loads must complete under 300ms (cached) or <1s on average.

**NFR-PERF-02**  
Search results must return within 500–800ms.

### 4.2 Security

- Passwords encrypted  
- Rate limiting on login  
- OAuth ready architecture  
- User data encrypted at rest  

### 4.3 Scalability

- Must support millions of users globally  
- Frontend served via CDN  
- SSR caching enabled  

### 4.4 Accessibility (AA-level future)

- Keyboard navigation  
- High-contrast themes  
- Screen-reader labels

---

## 5. Data Requirements

Key entities include:

- User  
- User Profile  
- Saved Payment Method  
- Booking  
- Ticket  
- Notifications  
- Support Request  

Detailed ERD stored in:

📄 `docs/architecture/data-models/customer-experience-data-model.md`

---

## 6. Future Enhancements

- Loyalty points  
- Gamification  
- Personalized route suggestions  
- Offline-first mobile apps  
- Predictive analytics  

---

## 7. Conclusion

The Customer Experience module defines all passenger-facing functionality of the Geo-Connect MaaS platform.  
It ensures seamless trip discovery, booking, payment, ticket management, and support.
