# Geo-Connect – Payments & Wallet SRS

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) defines the **Payments & Wallet Module** of the Geo-Connect MaaS platform.  
It covers all payment, refund, settlement, wallet, and reconciliation processes required to support bookings and provider payouts.

### 1.2 Scope

This module provides:

- Payment initiation  
- Payment provider integrations  
- Booking payment workflows  
- Refunds & partial refunds  
- Provider settlement accounts  
- Wallet system (optional MVP+)  
- Financial reporting  
- Ledger & audit trail management  

### 1.3 Definitions

**Payment Provider:** An external gateway such as Stripe, Paystack, Flutterwave, PayPal, etc.  
**Wallet:** An account for stored value (future phase).  
**Settlement:** Payment to service providers after commission.  
**Ledger:** Financial record-keeping system.  
**Transaction:** Any financial event (charge, refund, settlement).  
**Payout:** Money sent from Geo-Connect to a provider.

---

## 2. System Overview

The Payments Module consists of:

### 2.1 Payment Gateway Adapter Layer
- Supports multiple gateways  
- Uses a unified interface  
- Easily replaceable via configuration  

### 2.2 Payment Orchestration Engine
- Handles payment initiation  
- Manages confirmation callbacks  
- Ensures booking-payment consistency  

### 2.3 Refund Engine
- Manages full or partial refunds  
- Syncs refunds with provider systems  
- Tracks refund state  

### 2.4 Settlement Engine
- Computes provider payouts  
- Applies platform commission  
- Generates automated or manual payouts  

### 2.5 Wallet System (Future)
- Passenger wallet  
- Provider wallet  
- Prepaid balance  
- Promotions, vouchers, points  
- Offline credits  

### 2.6 Financial Logging & Audit Trail
- Ledger entries  
- Transaction-level traceability  
- Reconciliation logs  

---

## 3. Functional Requirements

---

# 3.1 Payment Initialization

### FR-PAY-01  
Passengers shall be able to pay for bookings using multiple payment providers.

### FR-PAY-02  
Supported payment types include:

- Card payment  
- Mobile money  
- Bank transfers  
- Wallet (future)  
- USSD (optional)  

### FR-PAY-03  
Each tenant shall configure its own payment provider keys.

### FR-PAY-04  
Payment initiation workflow:

1. Booking hold created  
2. Payment request generated  
3. Redirect to payment provider  
4. Provider callback to Geo-Connect  
5. Geo-Connect verifies transaction  
6. Booking confirmed or rejected  
7. Ticket issued  

### FR-PAY-05  
Sensitive payment data must never be stored except tokens.

---

# 3.2 Payment Gateway Adapter Interface

### FR-ADAPTER-01  
A unified adapter interface must exist:


### FR-ADAPTER-02  
Every provider integration must implement this interface.

### FR-ADAPTER-03  
Adapters must handle provider-specific:

- Parameters  
- Signatures  
- Redirect flows  
- API keys  
- Callback parsing  

---

# 3.3 Payment Verification

### FR-VERIFY-01  
System shall verify payment status with the provider before confirming bookings.

### FR-VERIFY-02  
Verification must include:

- Transaction ID  
- Amount  
- Currency  
- Customer reference  
- Provider reference  

### FR-VERIFY-03  
If verification fails:

- Booking remains pending  
- Reservation hold may expire  
- System shall notify customer  

---

# 3.4 Refunds

### FR-REFUND-01  
Refund workflows:

- Full refund  
- Partial refund  
- Manual refund (admin)  

### FR-REFUND-02  
Refunds must check:

- Provider cancellation rules  
- Payment provider refund capability  
- Treasury balance (provider payout not yet completed)  

### FR-REFUND-03  
Refund status values:

- Requested  
- Processing  
- Completed  
- Failed  

### FR-REFUND-04  
Refund records must include:

- Booking ID  
- Amount  
- Refund reference  
- Reason  
- Provider refund response  

---

# 3.5 Provider Settlement & Commission

### FR-SETTLE-01  
The system shall track:

- Total bookings per provider  
- Total charges  
- Geo-Connect commission  
- Provider receivable amounts  

### FR-SETTLE-02  
Commission models must support:

- Flat fee  
- Percentage fee  
- Tiered fees (future)  
- Per-mode fees  
- Promotional overrides  

### FR-SETTLE-03  
Settlement workflows:

- Automatic payouts (via gateway)  
- Manual payout triggers  
- Exportable settlement reports  

### FR-SETTLE-04  
Settlements must be tenant-specific and region-specific.

---

# 3.6 Wallet System (Future)

### FR-WALLET-01  
System shall support passenger wallet functionality.

### FR-WALLET-02  
Wallet actions:

- Debit (payments)  
- Credit (refunds, rewards)  
- Top-up (using payment gateway)  

### FR-WALLET-03  
Wallet balances must be real-time.

### FR-WALLET-04  
Provider wallets are optional for offline-capable providers.

---

# 3.7 Ledger & Financial Auditing

### FR-LEDGER-01  
All financial operations must create ledger entries.

### FR-LEDGER-02  
Ledger entries must include:

- Type (charge, refund, settlement)  
- Amount  
- Currency  
- Timestamp  
- Tenant  
- Provider  
- User  
- Booking reference  
- Associated transaction ID  

### FR-LEDGER-03  
Ledger must be immutable.

### FR-LEDGER-04  
Admins shall be able to view detailed reports.

---

## 4. Non-Functional Requirements

---

### 4.1 Performance

**NFR-PERF-01**  
Payment verification must occur within 300–600ms.

**NFR-PERF-02**  
Settlement generation must operate in batch mode for millions of records.

### 4.2 Security

**NFR-SEC-01**  
Platform must adhere to best practices for PCI DSS.

**NFR-SEC-02**  
API keys and webhook secrets must be encrypted.

**NFR-SEC-03**  
Sensitive responses must be redacted in logs.

### 4.3 Reliability

**NFR-REL-01**  
Payment callbacks must be idempotent.

**NFR-REL-02**  
Duplicate payments must be automatically detected.

**NFR-REL-03**  
Ledger must remain consistent even under failures.

### 4.4 Scalability

**NFR-SCALE-01**  
System must support 300 million+ payment-related transactions across regions.

**NFR-SCALE-02**  
Financial workflows must use queues for asynchronous processing.

---

## 5. Data Requirements

Key Entities:

- Payment Transaction  
- Payment Provider Config  
- Refund Request  
- Settlement Batch  
- Settlement Item  
- Wallet Account  
- Wallet Transaction  
- Ledger Entry  

Detailed ERD will be created in:

📄 `docs/architecture/data-models/payments-data-model.md`

---

## 6. Assumptions

- Providers must support refunds and settlements through APIs or manual process.  
- Not all providers support real-time payout.  
- Tenants may use different currencies.  
- FX conversions may be needed in multi-region contexts (future).

---

## 7. Future Enhancements

- Multi-currency wallet  
- FX conversion engine  
- Crypto payments  
- BNPL (Buy Now Pay Later)  
- Multi-tenant revenue share workflows  
- Automated fraud detection  
- PCI token vaulting  

---

## 8. Conclusion

The Payments & Wallet module ensures secure, scalable, and flexible financial operations across all regions and tenants.  
It is essential for handling transactions for bookings, refunds, settlements, and wallet operations in a massive-scale MaaS environment.
