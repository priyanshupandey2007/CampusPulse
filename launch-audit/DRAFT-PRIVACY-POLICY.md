# DRAFT – NOT LEGAL ADVICE: CampusPulse Privacy Policy

**Effective Date:** {{EFFECTIVE_DATE}}  
**Version:** 1.0.0-DRAFT  
**Entity Name:** {{LEGAL_ENTITY_NAME}}  
**Registered Address:** {{REGISTERED_ADDRESS}}  
**Contact Email:** {{BUSINESS_EMAIL}}  
**Data Protection Contact:** {{DATA_PROTECTION_OFFICER_EMAIL}}  

---

## 1. Overview and Our Role

This Privacy Policy explains how {{LEGAL_ENTITY_NAME}} ("CampusPulse", "we", "us", or "our") collects, uses, and safeguards information when educational institutions, faculty members, and students use the CampusPulse platform.

In most scenarios, your educational institution (university or college) is the **Data Controller** that determines the purposes and means of processing student data. CampusPulse acts as a **Data Processor** operating under a written Data Processing Agreement with your institution. Where we collect account administration details or platform telemetry directly, we act as a Data Controller.

---

## 2. Information We Collect

We adhere to the principle of **data minimization** and strictly collect only information necessary to deliver educational analytics and advising services.

### A. Academic & Telemetry Data (Ingested by Your Institution)
- **Student Identifiers:** University roll number, student reference ID, full name, institutional email address, department, batch, and section.
- **Academic Performance:** Cumulative Grade Point Average (CGPA), backlog count, and subject marks.
- **Attendance Records:** Subject-wise and aggregate attendance percentages.
- **Skill & Assessment Signals:** Coding test scores, aptitude assessments, and mock interview performance.
- **Learning Management System (LMS):** Course module completion percentages and portal access timestamps.
- **Extracurricular Activities:** Verified participation in campus clubs, hackathons, and certifications.

### B. Educator and User Account Data
- **Advisor Credentials:** Name, institutional email address, assigned department, and role permissions.
- **Intervention Records:** Structured coaching notes, action codes (e.g., Attendance Check-in, Coding Clinic), and target completion dates.

### C. Technical and Device Telemetry
- **Security & Access Logs:** IP address, browser type, operating system, and request timestamps (used strictly for rate limiting, brute-force mitigation, and security audit logs).
- **LocalStorage Data:** Active role selection, theme preference (`light`/`dark`), and user session token.

### D. Protected Categories Excluded
We do **not** collect, ingest, or process sensitive demographic attributes, including:
- Race, caste, or ethnic origin
- Religion or philosophical beliefs
- Biometric, genetic, or health data
- Political opinions or union membership
- Financial account details or credit card numbers

---

## 3. How We Use Information and Lawful Basis

We process data exclusively for legitimate educational and operational purposes:

| Purpose | Category of Data | Lawful Basis (GDPR Art. 6) |
| :--- | :--- | :--- |
| Calculating the Student Success Score | Academic, attendance, coding, and LMS metrics | Legitimate Interests / Educational Mission / Public Task |
| Identifying high-risk students via hard floors | Attendance, CGPA, and backlog thresholds | Educational Support / Legitimate Interests |
| Generating advisor action lists & intervention queues | Performance metrics and student identifiers | Performance of Institutional Contract |
| Platform security and rate limiting | IP address, request paths, timestamps | Legitimate Interests (System Security) |
| System audit trails and accountability | User IDs, actions performed, timestamps | Legal Obligation / Compliance |

---

## 4. No Unauthorized AI Training

We **do not** use student or faculty data to train, fine-tune, or improve external artificial intelligence models. The core CampusPulse scoring engine operates on deterministic mathematical rules. Zero data is shared with external commercial AI vendors (such as OpenAI, Anthropic, or Google) for model development.

---

## 5. Third-Party Service Providers (Subprocessors)

We disclose data only to trusted service providers bound by strict confidentiality and data protection agreements:
- **Cloud Infrastructure:** Render Services, Inc. (Hosting and database runtime in the United States, safeguarded by Standard Contractual Clauses).
- **Authentication:** Google Firebase (Identity management and session security).
- **Static Delivery:** jsDelivr (Client-side visualization library delivery).

A full, up-to-date list of subprocessors is available at our [Subprocessor Registry](file:///launch-audit/DRAFT-SUBPROCESSORS.md).

---

## 6. Data Retention and Deletion

We retain student records only as long as necessary to fulfill the institution's educational objectives:
- **Active Semester Data:** Retained during the academic year of enrollment.
- **Historical Trends:** Retained for the duration of the student's degree program plus one year, after which records are archived or anonymized.
- **Audit Logs:** Retained for 365 days for regulatory security verification.
- **Rate-Limiting Logs:** In-memory entries expire automatically after 60 seconds.

---

## 7. Your Privacy Rights

Depending on your jurisdiction (including EU/UK GDPR, California CCPA, and applicable state laws), you may have the following rights:
- **Access and Portability:** Request a copy of your personal data in a structured, machine-readable format.
- **Correction:** Request correction of inaccurate academic or biographical records through your university administration.
- **Erasure / Deletion:** Request deletion of personal accounts, subject to institutional retention obligations.
- **Restriction and Objection:** Object to non-essential processing or withdraw optional consent.

To submit a data access or deletion request, email {{DATA_PROTECTION_OFFICER_EMAIL}} or use our in-app privacy request interface. Requests are acknowledged within 5 business days and processed within 30 days.

---

## 8. Cookies and Tracking Technologies

CampusPulse uses **no third-party advertising cookies or tracking pixels**. 
Optional analytics (Firebase Analytics) are **disabled by default** and only activated if you explicitly grant consent through our Cookie Preferences banner. You may change or withdraw your consent at any time via the footer link.

---

## 9. Contact Us

If you have questions about this Privacy Policy or our data practices, please contact:
- **Data Protection Officer:** {{DATA_PROTECTION_OFFICER_EMAIL}}
- **Postal Address:** {{REGISTERED_ADDRESS}}

