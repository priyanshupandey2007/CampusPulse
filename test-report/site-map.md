# Site Map & Attack Surface Reconnaissance

**Target**: CampusPulse (Local: `http://127.0.0.1:8000`, Staging/Prod: `https://campuspulse-tau.vercel.app`)  
**Stack**: FastAPI (Python 3.12), SQLAlchemy, Uvicorn, Vanilla HTML5/CSS3/ES6, SQLite (local) / PostgreSQL (prod), Firebase Client Auth, Chart.js  
**Audit Date**: 2026-11-01  
**Branch**: `hardcore-test/2026-11-01`

---

## 1. Web Surfaces & Views

The frontend is an enterprise single-page application served from `apps/api/static/index.html` via FastAPI static mount with 12 distinct functional modules:

| View ID | Title / Role | Description | Input Elements / Controls |
|---|---|---|---|
| `#auth-overlay-screen` | Firebase & Demo Auth Modal | Role-based authentication modal overlaying entire app | Email, password, roll number, role tabs, demo login buttons, Google SSO, terms checkbox |
| `overview` | Executive Institutional Dashboard | High-level enrollment, retention rate, risk matrix, alerts | Filters (department, batch, section), date ranges |
| `students` | Student Roster & Deep Dive | Searchable table of student profiles, risk tiers, and EWMA trends | Search input, filter dropdowns, CSV export button |
| `interventions` | Closed-Loop Intervention Engine | Advisory actions, assignment of corrective playbooks | Intervention form (student ref, category, action, notes) |
| `analytics` | Cohort Readiness & Analytics | Predictive readiness curves, NAAC criterion distribution | Chart date toggles, batch selector |
| `naac` | Institutional SSR & Criteria Engine | Live NAAC grade simulator and criteria breakdown | What-if sliders, SSR export trigger, NAAC criteria cards |
| `sprints` | Student Learning Sprints | Micro-modular sprint tracker with in-progress learning | Module toggles, project sandbox link |
| `sandbox` | Python Code Execution Sandbox | Browser-based Python code test environment | Python editor textarea, "Run Code" execution button |
| `labs` | Virtual Lab Sessions | Interactive lab scheduling and submission tracker | Lab booking form, file upload dropzone |
| `trainers` | Trainer Scheduling | External expert booking calendar | Trainer select, date/time picker, booking button |
| `projects` | Capstone Project Bank | Assignment of enterprise challenge deliverables | Project assignment modal, team selector |
| `compliance` | Launch Audit & Privacy Controls | GDPR/DPDP/FERPA controls, telemetry and data purge | Data purge button, privacy request form |

---

## 2. API Endpoints Catalog

### Authentication & Core Infra
- `GET /` & `GET /dashboard` → Single page application (`index.html`)
- `GET /favicon.svg` & `GET /favicon.ico` → SVG Brand Favicon
- `GET /health` & `GET /api/v1/health` → JSON application health status
- `GET /health/db` → Database connection check
- `GET /health/ml` & `GET /api/v1/ml/status` → Supervised ML layer health
- `GET /api/v1/metrics` → Prometheus performance metrics
- `GET /api/v1/config/effective` → Deterministic configuration hash & params
- `GET /api/v1/auth/firebase-config` → Firebase client public credentials
- `POST /api/v1/auth/record-acceptance` → Record user TOS/Privacy agreement

### Data Ingestion & ETL
- `POST /api/v1/data-import/upload` & `POST /api/v1/ingest/upload` → Multipart file upload (.csv, .xlsx, .json)
- `POST /api/v1/ingest/preset/{preset_name}` → Load synthetic evaluation cohort
- `GET /api/v1/ingest/runs` → List historical ingestion batches
- `GET /api/v1/ingest/runs/{run_id}/cleaning-report` → Data cleaning & outlier report

### Students & Analytics
- `GET /api/v1/students` → Paginated student list with PII scoping
- `GET /api/v1/students/{student_ref}` → Individual student record
- `GET /api/v1/students/{student_ref}/explain` → Deterministic scoring breakdown (SHAP/feature contributions)
- `GET /api/v1/students/{student_ref}/trend` → Historical EWMA momentum telemetry
- `GET /api/v1/students/{student_ref}/export` → Student data export (GDPR Art. 20 portability)

### Interventions & Advisory
- `GET /api/v1/advisors/me/action-list` → Prioritized action backlog
- `GET /api/v1/advisors/me/interventions` → List advisor interventions
- `POST /api/v1/advisors/me/interventions` → Create new intervention
- `PATCH /api/v1/advisors/me/interventions/{intervention_id}` → Update intervention status/outcome
- `POST /api/v1/assistant/chat` → Advisory natural language intelligence agent
- `POST /api/v1/what-if` → Deterministic score simulation engine

### Academic, NAAC & Compliance
- `GET /api/v1/naac/overview` → Current institutional NAAC benchmark
- `GET /api/v1/naac/criteria` → All 7 NAAC criteria scores
- `GET /api/v1/naac/criteria/{criterion_id}` → Specific criterion metrics
- `GET /api/v1/naac/nep-matrix` → NEP 2020 alignment matrix
- `POST /api/v1/naac/simulate` → NAAC simulation projection
- `GET /api/v1/naac/ssr-export` → Institutional Self-Study Report export
- `GET /privacy` & `GET /api/v1/privacy/policy` → Privacy policy document
- `GET /terms` & `GET /api/v1/terms/service` → Terms of service document
- `POST /api/v1/privacy/requests` → Subject access / deletion request
- `POST /api/v1/admin/purge-expired-data` → Compliance data retention purge

### Code Execution & Nimbus Cloud
- `POST /api/v1/sandbox/run-code` → AST-verified Python sandbox
- `GET /api/v1/nimbus/cluster-status` → Cluster telemetry & node health
- `POST /api/v1/nimbus/exec-command` → Safe cloud cluster operational commands

---

## 3. Client-Side External Dependencies & Scripts

| Asset / Library | Source | Purpose | Integrity / CSP Check |
|---|---|---|---|
| Chart.js (v4.4.1) | `https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js` | Visual charts & radar plots | In CSP `script-src` |
| Firebase App (v10.8.0) | `https://www.gstatic.com/firebasejs/10.8.0/firebase-app-compat.js` | Client Firebase auth core | In CSP `script-src` (Patched) |
| Firebase Auth (v10.8.0) | `https://www.gstatic.com/firebasejs/10.8.0/firebase-auth-compat.js` | Email & Google OAuth sign-in | In CSP `script-src` (Patched) |
| Google Fonts (Inter) | `https://fonts.googleapis.com` / `https://fonts.gstatic.com` | Typography | In CSP `style-src` & `font-src` |

---

## 4. Environment Variables

| Variable | Default Value | Sensitivity | Usage |
|---|---|---|---|
| `DATABASE_URL` | `sqlite:///./campuspulse_local.db` | Medium | Primary SQLAlchemy engine connection |
| `DEBUG` | `false` | Low | Enables Swagger `/docs` and debug traces |
| `ALLOWED_ORIGINS` | `localhost:8000, 127.0.0.1:8000, campuspulse-tau-ten.vercel.app` | Medium | CORS allowed cross-origins |
| `RATE_LIMIT_MAX_PER_MIN` | `120` | Low | General IP request rate limit |
| `ENFORCE_STRICT_AUTH` | `false` | High | Toggles strict 401 requirement on all routes |
