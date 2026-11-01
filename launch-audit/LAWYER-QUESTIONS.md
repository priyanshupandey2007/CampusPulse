# Specific Questions for Legal Counsel

**Client:** CampusPulse Intelligence Systems  
**Date:** November 1, 2026  
**Subject:** Pre-Launch Compliance & Trust Review (Checklist v5.0)

---

### Question 1: Data Controller vs Data Processor Classification (§11)
CampusPulse is a B2B SaaS platform contracted by higher education institutions (universities and colleges) to analyze student academic performance, attendance, and placement readiness.
- In your opinion, is CampusPulse classified as a **Data Processor / Data Intermediary** operating under the instructions of the University (Data Controller / Data Fiduciary), or a joint controller?
- Is our draft Institutional Data Processing Agreement (`launch-audit/DRAFT-DPA.md`) sufficient to establish this processor status under the **EU GDPR (Art 28)** and the **Indian DPDP Act (Sec 8)**?

### Question 2: Eligibility & Age Assurance (§6)
Our Terms of Service restrict direct account creation to users aged 18 and older. However, higher education institutions frequently admit dual-enrollment or accelerated high school students aged 16 or 17.
- Under **FERPA** (US) and the **Indian DPDP Act** (Sec 9 - processing of children's data), does the university's institutional enrollment contract legally satisfy parental consent requirements for students under 18?
- Do we need an automated age gate during student portal access?

### Question 3: Cross-Border Transfers to US Cloud Subprocessors (§17)
CampusPulse utilizes Google Firebase (Authentication & Telemetry) and Vercel for web delivery, whose server infrastructure resides primarily in the United States.
- For institutions in the European Union and the United Kingdom, are Google's standard EU Model Contractual Clauses (Standard Contractual Clauses / SCCs) and the EU-US Data Privacy Framework (DPF) sufficient without supplementary measures?
- For institutions in India, does processing student telemetry on US servers comply with Section 16 of the Digital Personal Data Protection Act 2023?

### Question 4: Verifiable Consent Logging (§4)
We have implemented an unticked acceptance checkbox on the sign-in modal which logs the user identifier, document version (`1.0.0`), timestamp, client IP, and user-agent string into an immutable SQLite/PostgreSQL `AuditLog` table.
- Does this cryptographic and database audit record satisfy the evidentiary burden of demonstrable consent under **GDPR Art 7(1)** and **California Civil Code § 1798.100**?

### Question 5: Mandatory Institutional Retention vs Erasure Rights (§12, §13)
When a student submits an erasure request under GDPR Art 17 or DPDP Sec 12, higher education institutions are legally mandated to retain academic records, examination grades, and accreditation data for statutory periods (e.g. 5–10 years).
- Does our policy correctly establish that institutional academic records are exempt from unilateral student deletion requests while the student is enrolled, deferring final deletion authority to the University?
