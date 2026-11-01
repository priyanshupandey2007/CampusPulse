# Data-Flow Inventory: CampusPulse

**Date:** 2026-11-01  
**Product:** CampusPulse (v5.0.0)  
**Classification:** Higher Education Student Success and Placement Readiness Platform (B2B SaaS)  

This inventory documents all personal data fields, storage keys, cookies, external network calls, logging fields, and third-party vendors identified across `apps/`, `packages/`, `services/`, and `adapters/`.

---

## 1. Personal Data Fields Collected and Processed

| Data Element | Data Subject | Collection Point | Storage Location | Processing Purpose | Legal Basis (EU/UK GDPR) | Retention Period |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Student Roll Number** | Student | Ingestion CSV/XLSX (`/api/v1/ingest/upload`) | `students.roll_number` | Unique university identifier for academic matching | Legitimate Interests / Public Task | Duration of enrollment + 1 academic year |
| **Student Full Name** | Student | Ingestion CSV/XLSX | `students.name` | Human display for faculty advisor workstations | Legitimate Interests / Contract | Duration of enrollment + 1 academic year |
| **Student Email** | Student | Ingestion CSV/XLSX | `students.email` | Notification routing and student portal access | Legitimate Interests / Contract | Duration of enrollment + 1 academic year |
| **Department & Batch** | Student | Ingestion CSV/XLSX | `students.department`, `students.batch` | Cohort-level grouping, NAAC metrics | Legitimate Interests / Contract | Duration of academic program |
| **Academic Metrics (CGPA, Backlogs)** | Student | Ingestion CSV/XLSX | `weekly_metrics.academic_index` | Calculate Academic Sub-Index ($I_{\text{acad}}$) | Legitimate Interests / Educational mission | Duration of academic program |
| **Attendance Records** | Student | Ingestion CSV/XLSX | `weekly_metrics.attendance_index` | Attendance floor checks and absenteeism scoring | Legitimate Interests / Educational mission | 1 academic year |
| **Coding Assessment Scores** | Student | Ingestion CSV / Editor submit | `weekly_metrics.placement_index` | Placement readiness calculation ($I_{\text{place}}$) | Legitimate Interests / Consent | 1 academic year |
| **LMS Completion & Logins** | Student | Ingestion CSV/XLSX | `weekly_metrics.lms_index` | Course portal engagement tracking | Legitimate Interests / Contract | 1 academic year |
| **Faculty Advisor Name & Email** | Educator | Auth Header / DB Seed | `advisors.name`, `advisors.email` | Advisor identity and intervention attribution | Contractual necessity | Duration of employment |
| **Intervention Notes & Action Codes** | Student / Advisor | Faculty Intervention Form | `interventions.notes`, `action_code` | Closed-loop mentoring tracking and support | Educational support / Legitimate Interests | Duration of student enrollment |
| **Client IP Address** | User (Any) | HTTP Request Headers | In-memory `RATE_LIMIT_STORE` | Rate limiting & brute-force protection | Legitimate Interests (Security) | Sliding window 60 seconds (ephemeral) |
| **Audit Actor & Action** | User (Any) | API Mutation Endpoints | `audit_log.actor_id`, `audit_log.action` | Regulatory audit trail and accountability | Legal Obligation / Legitimate Interests | 365 days |

### Protected Attributes Excluded by Policy
The following categories are **never** collected or ingested:
- Race, ethnic origin, or caste
- Religious or philosophical beliefs
- Political opinions or union membership
- Genetic, biometric, or health/medical data
- Sexual orientation or gender identity
- Socio-economic or financial background (bank accounts, credit cards)

---

## 2. Browser Storage & Cookie Inventory

| Identifier | Type | Origin / Provider | Purpose | Strictly Necessary? | Default State | Lifetime |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| `campuspulse_active_role` | LocalStorage | First-party (CampusPulse) | Stores active view role (`faculty`, `student`, `dean`, `hod`) | Yes (Functional UI) | Set on role switch | Persistent until logout |
| `campuspulse_auth_user` | LocalStorage | First-party (CampusPulse) | Stores authenticated user profile summary | Yes (Authentication) | Set on login | Session / Cleared on logout |
| `campuspulse_consent_v1` | LocalStorage | First-party (CampusPulse) | Stores cookie and tracking consent choices | Yes (Consent record) | Set on user choice | 365 days |
| `theme` | LocalStorage | First-party (CampusPulse) | User interface theme preference (`light` / `dark`) | Yes (Accessibility/UI) | `light` | Persistent |
| `campuspulse_firebase_config`| LocalStorage | First-party (CampusPulse) | Local Firebase connection parameters | Yes (Configuration) | Local cache | Persistent |
| `_ga`, `_ga_*` | Cookie | Google Firebase Analytics | Anonymous telemetry and usage metrics | No (Analytics) | **OFF** until explicit consent | 2 years (if consented) |

---

## 3. Third-Party Vendors and External Services

| Vendor / Service | Role | Location / Hosting | Data Transferred | Transfer Mechanism | DPA Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Render Services, Inc.** | Cloud Infrastructure & Hosting | US (Oregon / Ohio) | Application runtime, database volumes | Standard Contractual Clauses (SCCs) | Needs Human (Corporate DPA) |
| **Google Cloud / Firebase** | Authentication & Optional Analytics | Global / US | User email, auth credentials, client IP | EU-US Data Privacy Framework / SCCs | Needs Human (Google Cloud DPA) |
| **Google Fonts** (Static) | CDN Fonts Delivery | Global CDN | Browser IP, User-Agent (HTTP header) | Legitimate Interests / Anonymous CDN | Standard Terms |
| **jsDelivr (ProspectOne)** | Open-source Library CDN (Chart.js) | Global CDN | Browser IP, User-Agent (HTTP header) | Legitimate Interests / Anonymous CDN | Standard Terms |

---

## 4. Application Logging Fields

- `services/cleaning/cleaner.py`: Logs `run_id`, timestamp, row counts, and data anomaly counts.
- `apps/api/main.py`: Audit logs write `actor_id`, `actor_role`, `action`, `target_type`, `target_id`, `created_at`. No passwords, tokens, or raw secrets are written to logs.
- Prometheus Metrics (`/api/v1/metrics`): Aggregated numerical gauges and counters only; strictly strips all names, emails, and student references.

