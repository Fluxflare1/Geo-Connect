# Geo-Connect – Identity & Access Management (IAM) System SRS

## 1. Introduction

### 1.1 Purpose
This Software Requirements Specification (SRS) defines the **Identity & Access Management (IAM)** system for Geo-Connect.

The IAM module handles:

- Authentication  
- Authorization  
- User account management  
- Role-Based Access Control (RBAC)  
- Multi-tenant identity separation  
- Admin/provider/user identity flows  
- Security/session management  

### 1.2 Scope
Covers identity for:

- Passengers  
- Providers  
- Tenants  
- Platform administrators  
- Partner systems  
- Validator devices  
- Internal services (service-to-service)  

### 1.3 Definitions
**RBAC:** Role-Based Access Control.  
**Tenant:** A client using the Geo-Connect platform.  
**Provider:** Transportation operator.  
**Access Token:** JWT token used to authenticate requests.  
**Single Sign-On (SSO):** Unified authentication across systems.  

---

## 2. System Overview

The IAM system includes:

### 2.1 Authentication Layer
- Email/password  
- Phone/OTP  
- OAuth2 / OIDC  
- Social login (future)  
- Service-to-service tokens  

### 2.2 Authorization Layer
- RBAC (Role-Based Access Control)  
- Provider-level permissions  
- Tenant-level isolation  
- Fine-grained access policies  

### 2.3 User Directory
- Passenger directory  
- Provider staff directory  
- Tenant admin directory  
- Internal system accounts  

### 2.4 Security & Session Management
- Token issuance  
- Refresh tokens  
- Session expiration  
- Device tracking  

---

## 3. Functional Requirements

---

# 3.1 Authentication

### FR-AUTH-01  
Supported login methods:

- Email + password  
- Phone number + OTP  
- OAuth2/OIDC provider login  
- Device-based authentication for validators  

### FR-AUTH-02  
Passwords must:

- Follow strength rules  
- Be hashed using strong algorithms (bcrypt/argon2)  
- Never be stored as plain text  

### FR-AUTH-03  
MFA (Multi-Factor Authentication):

- Optional for admins  
- Mandatory for platform super admins  

---

# 3.2 Authorization (RBAC + Policies)

### FR-AUTHZ-01  
System must support RBAC with predefined roles:

#### Platform-level:
- Super Admin  
- Finance Admin  
- Technical Admin  
- Auditor  

#### Tenant-level:
- Tenant Owner  
- Tenant Admin  
- Support  
- Analyst  

#### Provider-level:
- Provider Manager  
- Operator  
- Support  

#### Passenger-level:
- Standard User  
- Corporate User (optional)  

### FR-AUTHZ-02  
Custom roles may be created by tenants and providers.

### FR-AUTHZ-03  
Access policies must define:

- Allowed endpoints  
- Allowed modules  
- Data restrictions  
- Provider/Tenant scoping  

---

# 3.3 User Management

### FR-USER-01  
Platform must allow:

- Create/update/delete users  
- Assign/remove roles  
- Assign provider/tenant scope  
- Manage user status (active, suspended, deleted)  

### FR-USER-02  
Users can update:

- Profile info  
- Contact details  
- Password  
- Notification preferences  

### FR-USER-03  
User activity logs must be maintained.

---

# 3.4 Tenant & Provider Isolation

### FR-ISO-01  
Each tenant’s users and data must be isolated.

### FR-ISO-02  
Provider accounts have:

- Access only to their fleet/routes  
- Read-only access to shared modules  

### FR-ISO-03  
Cross-tenant visibility is strictly forbidden.

---

# 3.5 Token Management

### FR-TOKEN-01  
IAM must issue:

- JWT access tokens  
- Refresh tokens  
- Device tokens for validators  
- Service-to-service tokens  

### FR-TOKEN-02  
Token data includes:

- User ID  
- Tenant ID  
- Provider ID  
- Roles  
- Permissions  
- Expiration  

### FR-TOKEN-03  
Token revocation required for:

- Password change  
- User suspension  
- Role change  
- Security breach  

---

# 3.6 Session Management

### FR-SESSION-01  
System must track active sessions:

- Device type  
- Location (approximate)  
- Last login time  

### FR-SESSION-02  
Auto-expiration rules:

- Passenger sessions: 7 days  
- Administrator sessions: 12 hours  
- Validator device sessions: configurable  

---

# 3.7 Audit Logging

### FR-AUDIT-01  
IAM logs:

- Login attempts  
- Access denials  
- Role changes  
- User creation/deletion  
- Token invalidations  

### FR-AUDIT-02  
Audit logs must be immutable.

---

# 3.8 Security Features

### FR-SECURE-01  
Account lockout after repeated failures.

### FR-SECURE-02  
IP/device anomaly detection.

### FR-SECURE-03  
Encryption:

- Personal data  
- Credentials  
- Sensitive tokens  

### FR-SECURE-04  
Compliance:

- GDPR  
- Data residency  
- Privacy rules  

---

# 3.9 SSO & Integrations (Future)

### FR-SSO-01  
Support future integrations with:

- Google Workspace  
- Microsoft Azure AD  
- SAML providers  

### FR-SSO-02  
Support delegated admin roles.

---

## 4. Non-Functional Requirements

### 4.1 Performance
- Token issuance < 150ms  
- Login < 500ms  
- User directory query < 200ms  

### 4.2 Scalability
- Millions of concurrent authenticated users  
- Distributed token validation  
- Regional authentication clusters  

### 4.3 Security
- OWASP compliance  
- Secure token signing  
- Threat detection & alerts  

### 4.4 Reliability
- Automatic failover  
- Multi-region redundancy  
- Zero downtime for IAM core  

---

## 5. Data Requirements

IAM stores:

- User profiles  
- Hashed passwords  
- Roles & permissions  
- Token metadata  
- Audit logs  
- Tenant/provider scopes  

---

## 6. Future Enhancements

- Biometric login  
- Behavioral authentication  
- Passwordless login  
- AI-based access anomaly detection  

---

## 7. Conclusion

The IAM module ensures secure, scalable, and efficient identity management for Geo-Connect.  
It supports complex roles, multi-tenant architectures, multi-provider ecosystems, and a high-security authentication framework suitable for a global MaaS platform.
