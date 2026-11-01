# CampusPulse Pre-Launch Human Action Register

This document lists all action items that require human decisions, legal counsel, or operational execution before the production launch of CampusPulse.

---

## 1. Legal Counsel
- [ ] **Review & Finalize Privacy Notice**: Replace placeholders `{{LEGAL_ENTITY_NAME}}`, `{{REGISTERED_ADDRESS}}`, `{{DPO_EMAIL}}`, `{{CONTACT_EMAIL}}` in `launch-audit/DRAFT-PRIVACY-POLICY.md`.
- [ ] **Review & Finalize Terms of Service**: Replace placeholders `{{GOVERNING_LAW}}`, `{{ARBITRATION_CITY}}`, `{{CONTACT_EMAIL}}` in `launch-audit/DRAFT-TERMS-OF-SERVICE.md`.
- [ ] **Data Processing Agreement (DPA)**: Finalize `launch-audit/DRAFT-DPA.md` as the standard addendum for collegiate institutional client contracts.
- [ ] **Lawful Basis Opinion (§11)**: Provide written confirmation of lawful basis under GDPR/DPDP (Controller-Processor relationship with colleges vs Legitimate Interests).
- [ ] **Cross-Border Transfer Mechanisms (§17)**: Confirm EU Standard Contractual Clauses (SCCs) and Indian DPDP cross-border data transfer documentation for US cloud hosting (Firebase / Vercel).

---

## 2. Founder / Business
- [ ] **Institutional Contract Addendum**: Ensure all college onboarding packets include the finalized Institutional DPA.
- [ ] **FERPA / Minor Enrollment Check (§6)**: Verify with participating colleges whether any high school dual-enrollment students under 18/16 are enrolled in participating cohorts.
- [ ] **Subprocessor Execution (§18)**: Confirm executed DPAs with Google (Firebase) and Vercel.
- [ ] **DPO / Privacy Point of Contact**: Designate an internal or external Data Protection Officer email address (`dpo@campuspulse.edu`).

---

## 3. DevOps & Infrastructure
- [ ] **Backup Purge Lifecycle (§14)**: Configure automated deletion lifecycle for PostgreSQL database backups so that deleted student records are permanently purged after 90 days.
- [ ] **Production Secrets & Keys**: Replace default development secrets (`STUDENT_ID_SALT`, Firebase API credentials) with production KMS/Vault managed credentials.
- [ ] **TLS Certificate Verification (§19)**: Ensure automated renewal via Let's Encrypt / Cloudflare with HSTS preloading enabled on the production domain.

---

## 4. Product & Design
- [ ] **Screen Reader Accessibility Audit (§20)**: Conduct an end-to-end screen reader audit using NVDA or VoiceOver on the Student 360 and NAAC Radar chart views.
- [ ] **12-Month Cookie Re-Consent Prompt (§9)**: Schedule automatic consent re-evaluation after 365 days of stored consent.

---

## 5. Marketing
- [ ] **Claims Register Adherence (§27–§31)**: Ensure all external marketing collateral adheres to the verified claims register in `launch-audit/REPORT.md` (no false SOC 2 badges, no artificial countdowns, no unverified stats).

---

## Placeholders Requiring Concrete Business Values
| Placeholder | Purpose | File Location |
|---|---|---|
| `{{LEGAL_ENTITY_NAME}}` | Official registered company name | `DRAFT-PRIVACY-POLICY.md`, `DRAFT-TERMS-OF-SERVICE.md`, `DRAFT-DPA.md` |
| `{{REGISTERED_ADDRESS}}` | Registered corporate office address | `DRAFT-PRIVACY-POLICY.md`, `DRAFT-TERMS-OF-SERVICE.md`, `DRAFT-DPA.md` |
| `{{COMPANY_REGISTRATION_NUMBER}}` | Company registration / CIN / corporate ID | `DRAFT-TERMS-OF-SERVICE.md` |
| `{{DPO_EMAIL}}` | Dedicated Data Protection Officer inbox | `DRAFT-PRIVACY-POLICY.md`, `DRAFT-DPA.md` |
| `{{CONTACT_EMAIL}}` | General legal & support email | `DRAFT-PRIVACY-POLICY.md`, `DRAFT-TERMS-OF-SERVICE.md` |
| `{{GOVERNING_LAW}}` | Jurisdiction governing institutional disputes | `DRAFT-TERMS-OF-SERVICE.md`, `DRAFT-DPA.md` |
| `{{ARBITRATION_CITY}}` | Seat of arbitration | `DRAFT-TERMS-OF-SERVICE.md` |
