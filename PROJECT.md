# Project: CampusPulse — Claude Court Case #002 Fixes

## Architecture
- **Backend**: FastAPI web service (`apps/api/main.py`), pure AST domain scoring engine (`packages/domain/scores.py`), rules engine (`config/rules.yaml`), and enrichment services (`services/enrichment/rules_layer.py`, `services/enrichment/ml_layer.py`).
- **Data Ingestion**: Multi-format data loader (`services/ingestion/loader.py`, `services/pipeline.py`) supporting CSV, Excel (.xlsx/.xls) via `POST /api/v1/ingest/upload` and `POST /api/v1/data-import/upload`.
- **Frontend**: Single-page application (`apps/api/static/index.html`) driven by role-based access control (`ROLE_METADATA`), dynamic tab routing (`switchNav`), and real-time API integrations.
- **Integrity & Verification**: 100% deterministic pure AST scoring core, strict local execution, zero git push, and 80 existing pytest tests in `tests/` and `test-report/regression-tests/`.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Advisor Navigation Focus | Elevate advisor early-warning triage, student 360, and intervention tracking front-and-center | M2 | R1, Court Case §2, 4 |
| 2 | Secondary Student Labs | De-emphasize peripheral student tools (coding lab, mock interviewer, code editor, AI mentor) to secondary navigation | M2 | R1, Court Case §4 |
| 3 | Primary CSV/Excel Ingestion | Elevate CSV/Excel file upload as the primary ingestion entry point in UI headers and onboarding | M2 | R4, Court Case §5 |
| 4 | Deterministic Core Invariance | Ensure all student success calculations remain 100% deterministic pure AST arithmetic | M1 | R2, Court Case §2 |
| 5 | ML Fairness Proxy Repositioning | Decouple and position ML strictly as an optional, audited fairness proxy add-on (disagreement detector) | M1, M2 | R2, Court Case §2, 4 |
| 6 | Configurable Alert Thresholds API | Implement GET/PUT `/api/v1/config/thresholds` defaulting standard attendance alert to 75% and floor to 57% | M1 | R3, Court Case §4 |
| 7 | Configurable Thresholds UI | Expose threshold configuration controls in advisor settings/dashboard with 75% standard default | M2 | R3, Court Case §4 |
| 8 | 57% Emergency Hard Floor Rationale | Provide explicit mathematical derivation (Week 9 point-of-no-return) in docs and UI tooltips | M1, M2 | R3, Court Case §1, 4 |
| 9 | NAAC Accreditation Softening | Soften claims from "NAAC A++ forecasting" to "NAAC SSR Readiness & Evidence Dossier" | M2 | R4, Court Case §5 |
| 10 | NAAC Metric Validation & Disclaimers | Add statutory disclaimers and metric validation (Criteria 2.6/5.1) while preserving internal test keys | M2 | R4, Court Case §5 |
| 11 | Zero Regressions (80 Pytest Tests) | Ensure all 80 existing pytest tests pass continuously | M3, M4 | R5, Acceptance Criteria |
| 12 | New Test Suite Expansion | Add comprehensive unit tests for threshold API, ingestion path, and score explainability | M3, M4 | R5, Acceptance Criteria |
| 13 | Local Execution Strict Invariant | Enforce strict local execution with zero git push | M1-M4 | R5, System Prompt |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Backend Configurable Thresholds & ML Fairness Proxy API | Implement configurable threshold API (75% standard, 57% emergency), ML proxy metadata, 57% mathematical rationale in documentation | none | DONE |
| M2 | Frontend Navigation, Ingestion Hero & NAAC Rebranding | Restructure index.html: advisor primary, student labs secondary, CSV/Excel upload hero, threshold UI controls, ML proxy UI, NAAC SSR Dossier | M1 | DONE |
| M3 | Test Suite Expansion & Pyproject Configuration | Add pyproject.toml testpaths, add unit tests for threshold API, ingestion, score explainability, and NAAC contract | M1, M2 | DONE |
| M4 | Final E2E Verification, Adversarial Testing & Forensic Audit | Run all 80+ pytest tests, verify zero regressions, verify zero git push, conduct adversarial verification and forensic integrity audit | M1, M2, M3 | DONE |

## Interface Contracts
### Frontend ↔ Backend: Configurable Thresholds API
- Endpoint: `GET /api/v1/config/thresholds`
  - Response:
    ```json
    {
      "attendance_standard_min": 75.0,
      "attendance_emergency_min": 57.0,
      "cgpa_warning_min": 6.0,
      "cgpa_emergency_min": 4.7,
      "backlog_warning_max": 2,
      "backlog_emergency_max": 3,
      "institutional_policy_default": "UGC/AICTE 75% Standard",
      "emergency_floor_rationale": "Week 9 point of mathematical impossibility (0.60 * 57% + 0.40 * 100% = 74.2% < 75%)"
    }
    ```
- Endpoint: `PUT /api/v1/config/thresholds`
  - Request:
    ```json
    {
      "attendance_standard_min": 75.0,
      "attendance_emergency_min": 57.0,
      "cgpa_warning_min": 6.0,
      "cgpa_emergency_min": 4.7
    }
    ```
  - Response: `{"status": "updated", "thresholds": { ... }}`
  - Error Handling: Validation error HTTP 422 if `attendance_emergency_min >= attendance_standard_min` or values out of bounds [0, 100].

### Frontend ↔ Backend: Primary Ingestion Path
- Endpoint: `POST /api/v1/ingest/upload` and `POST /api/v1/data-import/upload`
  - Content-Type: `multipart/form-data` (file: .csv, .xlsx, .xls)
  - Limit: 15 MB
  - Response: `{"status": "success", "rows_ingested": int, "pipeline_id": str}`

### Backend Domain ↔ NAAC Evaluator Contract
- Internal dictionary outputs: `d["grade"]` retained as `"A++"` for test compatibility.
- Display metadata: Added `"framework_title": "NAAC SSR Readiness & Evidence Dossier"`, `"statutory_disclaimer": "Statutory accreditation is determined exclusively by official NAAC peer-team evaluation."`

## Code Layout
- `apps/api/main.py`: FastAPI routes, threshold endpoints, ingestion upload handlers.
- `apps/api/static/index.html`: SPA frontend, navigation hierarchy, secondary labs, ingestion hero, NAAC evidence dossier UI.
- `packages/domain/scores.py`: Pure AST arithmetic scoring engine, tier classification, priority ranking.
- `services/enrichment/ml_layer.py`: Audited fairness proxy add-on, demographic parity checks.
- `STUDENT_SUCCESS_SCORE.md`, `README.md`: Formal documentation of 57% emergency hard-floor mathematical derivation.
- `tests/`: Existing 66 pytest tests.
- `test-report/regression-tests/`: Existing 14 pytest regression tests.
- `tests/unit/test_thresholds_and_explainability.py`: New comprehensive unit tests for threshold API, explainability, and ingestion.
