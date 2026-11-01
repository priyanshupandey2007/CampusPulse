# Audit Assumptions & Context: CampusPulse

**Date:** 2026-11-01  
**Project:** CampusPulse (v5.0.0)  

This document records the foundational technical and business assumptions inferred from the codebase, configuration, and architectural design of CampusPulse.

---

## 1. Project Context & Positioning

- **Product Name:** CampusPulse
- **One-Line Description:** Deterministic student success, risk identification, and placement readiness platform for higher education institutions.
- **Primary Audience:** B2B Higher Education Institutions (Universities, Engineering Colleges, Department Deans, HODs, Faculty Advisors, Placement Officers, and University Students).
- **Target Jurisdictions:** India (primary institutional customer base, NIRF/NAAC accreditation context), United States (FERPA and state privacy regulations), European Union / United Kingdom (GDPR / ePrivacy alignment for global deployments).

---

## 2. Inferred Business Model & Monetization

- **Business Model:** B2B Institutional SaaS license (departmental or campus-wide annual subscription).
- **Billing Mechanism:** Enterprise procurement agreements, institutional purchase orders, and direct bank transfers.
- **Consumer Transactions:** None. There are no consumer checkouts, credit card storage, payment gateways (Stripe/PayPal), or automatic recurring card renewals in the codebase.
- **Assumed Applicability for §5, §24, §25, §26:** Marked **N/A** because consumer distance contracts, drip pricing, and negative-option recurring subscriptions do not apply to direct enterprise software licensing.

---

## 3. Data Subject Population & Children's Regulations (§14)

- **Target User Age:** Undergraduate and postgraduate college students, typically aged 18 to 24+.
- **Children's Policy:** The application is not directed toward, marketed to, or intended for children under 13 (US COPPA) or minors under 16 (EU GDPR Article 8).
- **Eligibility Assumption:** Enrollment eligibility is restricted to admitted college students and authorized university personnel. Terms of service establish a minimum age requirement of 18 years.

---

## 4. Artificial Intelligence & Machine Learning Architecture (§15, §32)

- **Scoring Engine:** The production student scoring pipeline (`packages/domain/`) uses pure Python deterministic formulas (arithmetic weights, min/max clamping, and floor rules). It makes zero runtime calls to external LLMs or third-party generative AI APIs.
- **Machine Learning Layer (`services/enrichment/ml_layer.py`):** Uses offline trained linear proxy models strictly as a secondary disagreement check (`confidence_note`).
- **Chatbot Assistant (`/api/v1/assistant/chat`):** A read-only rule-based advisor assistant responding to keyword queries with pre-aggregated metrics.
- **Assumed Applicability for §15:** Marked **Pass** because user data is never sent to external AI vendors for model training or fine-tuning.

---

## 5. User-Generated Content & DMCA (§35)

- **Content Ingestion:** The platform processes structured CSV/XLSX spreadsheets uploaded by authorized faculty advisors containing academic rosters and test marks.
- **Public Hosting:** Students and users do not publish public social media posts, public videos, blog articles, or media files accessible to the outside internet.
- **Assumed Applicability for §35:** Marked **N/A** because safe-harbor protection under 17 U.S.C. §512(c) applies to services hosting publicly accessible user content. A standard copyright notice and contact point is nonetheless maintained in the terms.

---

## 6. Placeholders Requiring Human / Legal Completion

The following marked placeholders are used throughout the legal drafts and reports:
- `{{LEGAL_ENTITY_NAME}}`
- `{{REGISTERED_ADDRESS}}`
- `{{BUSINESS_EMAIL}}`
- `{{DATA_PROTECTION_OFFICER_EMAIL}}`
- `{{COMPANY_REGISTRATION_NUMBER}}`
- `{{GOVERNING_LAW_JURISDICTION}}`

