# Handoff Report: UI, Navigation, Ingestion & Accreditation Claims Survey

**Agent**: teamwork_explorer (`explorer_survey_2`)  
**Parent / Recipient**: 66ad5db5-2085-4f27-86e7-392d30b57f3a  
**Milestone**: Investigation & Survey Complete  
**Date**: 2026-11-03  

---

## 1. Observation

1. **Frontend Layout and Navigation Components**:
   - Primary frontend file: `apps/api/static/index.html` (12,156 lines, ~723 KB).
   - Sidebar container: `<aside class="sidebar">` at lines 2959–3169; navigation links `<nav class="sidebar-nav">` at lines 2974–3162.
   - Topbar header: `<header class="top-navbar">` at lines 3175–3245.
   - Client routing function: `switchNav(viewId)` defined at lines 7438–7512, which validates RBAC via `ROLE_METADATA[role].allowedViews` and activates target `<div id="view-{viewId}" class="tab-view">`.
   - RBAC rules: `ROLE_METADATA` defined at lines 6924–7065 covering 5 roles (`dean`, `hod`, `teacher`/`advisor`, `student`, `recruiter`). Declarative hiding via CSS: `body[data-active-role="student"] [data-roles]:not([data-roles~="student"]) { display: none !important; }` at lines 1957–1965.

2. **Advisor Workflows & Peripheral Tools**:
   - Advisor Early-Warning & Priority Triage: `#view-action-list` at lines 3249–3426, driven by `loadActionList()` fetching `GET /api/v1/advisors/me/action-list?limit=50`. Includes attendance/CGPA alert banner (lines 3278–3287) and triage table (lines 3362–3380).
   - Intervention Tracking: `#view-interventions-os` at lines 5376–5446, driven by `loadInterventionsOS()` fetching `GET /api/v1/advisors/me/interventions`.
   - Peripheral student tools currently located directly in primary student sidebar (`apps/api/static/index.html:2998-3022`) under `"Skill & Career Hub"`:
     - `learn-modules`: Placement Prep Modules (`#view-learn-modules`, line 4445)
     - `lab-practice`: Coding Practice Labs (`#view-lab-practice`, line 4711)
     - `ai-mentor`: AI Academic Mentor (`#view-ai-mentor`, line 4382)
     - `ai-interviewer`: Mock Interviewer (`#view-ai-interviewer`, line 4410)
     - `code-editor`: Online Code Editor (`#view-code-editor`, line 4455)
     - `project-bank`: Capstone Projects (`#view-project-bank`, line 4821)

3. **Data Ingestion Pathways**:
   - Backend routes: `POST /api/v1/ingest/upload` and `POST /api/v1/data-import/upload` in `apps/api/main.py:458-546` accept `.xlsx`, `.xls`, `.csv` (`ALLOWED_INGEST_EXTENSIONS`). Validates magic bytes (ZIP header `PK\x03\x04` for Excel; non-binary check for CSV), enforces 15 MB limit, and triggers `services.pipeline.execute_pipeline(temp_path, db)`.
   - Demonstration presets: `POST /api/v1/ingest/preset/{preset_name}` in `apps/api/main.py:548-572` loads Section C, Section D, or sample files.
   - Frontend UI: `#view-ingestion-pipeline` at lines 5539–5662. Custom file upload is currently a 50% split card paired alongside presets under "Operations > Data Integration". The main advisor dashboard (`#view-action-list`) lacks an immediate upload action trigger.

4. **Accreditation Claims**:
   - Prominent claims:
     - Sidebar student nav: `College Accreditation (NAAC)` with badge `A++` (lines 2994–2995).
     - Sidebar advisor nav: `Accreditation & NEP 2020` with badge `Grade A++ (3.65)` (lines 3066–3067).
     - Topbar button: `NAAC A++ (3.65)` (line 3188).
     - College reports banner: `NAAC Revised Accreditation Framework (RAF) Assessment` with `Projected Institutional CGPA: 3.65 / 4.00 (Grade A++ Distinction)` (line 3479).
     - Evaluator view: `NAAC Accreditation & NEP 2020 Platform` (line 3828) with hero display `<span id="naac-hero-grade">A++</span>` (line 3865).
   - Test suite invariant: `tests/api/test_naac_api.py:26, 89` and `tests/unit/test_naac_domain.py:27, 60` assert `d["grade"] == "A++"`. `pytest` passes with 66/66 tests when calculation functions retain standard NAAC letter grades.

---

## 2. Logic Chain

1. **Hierarchy Logic**:
   - *Observation*: The core advisor mission centers on early-warning risk triage and student support plans. Peripheral student tools (`code-editor`, `ai-interviewer`, `lab-practice`) are currently colocated with academic profiles in the primary sidebar.
   - *Deduction*: De-emphasizing peripheral tools by moving them under a clear secondary section title (`"Student Practice Labs (Secondary)"`) while keeping all DOM IDs, `ROLE_METADATA.allowedViews`, and `switchNav` targets intact fulfills Requirement R1 with zero regressions.

2. **Ingestion Logic**:
   - *Observation*: The backend ingestion engine already has production-grade validation for Excel and CSV, but advisors currently have to navigate through "Operations > Data Integration" to find it, where it shares space with demo presets.
   - *Deduction*: Placing an "Upload Dataset (CSV/Excel)" action button in the `#view-action-list` header and reorganizing `#view-ingestion-pipeline` so custom upload is the dominant hero card elevates CSV/Excel ingestion to the primary platform entry point without requiring any backend pipeline restructuring.

3. **Accreditation Softening Logic**:
   - *Observation*: Marketing internal software projections as official "NAAC A++ forecasting" violates institutional audit standards because statutory accreditation is awarded solely by official NAAC peer-teams. However, existing test cases verify `d["grade"] == "A++"`.
   - *Deduction*: We must soften claims strictly at the presentation, label, badge, and copy layer—reframing the module as **"NAAC SSR Readiness & Evidence Dossier"** and adding clear metric validation and peer-assessment disclaimers—without modifying internal dictionary schema keys or mathematical grade-mapping functions.

---

## 3. Caveats

1. **In-Flight Working Tree Modifications**:
   - `git diff` shows localized edits in `apps/api/main.py` (sandbox test case validation) and `apps/api/static/index.html`. Implementers must ensure subsequent changes merge cleanly without overwriting peer adjustments.
2. **Deterministic Hash Invariance**:
   - `scripts/boot_check.py` checks `config_hash` and `targets_hash`. UI adjustments in `index.html` do not affect YAML config hashes, but any edits to `config/config.yaml` or `config/rules.yaml` will alter the boot hash.

---

## 4. Conclusion

The CampusPulse platform is structurally sound, highly responsive, and well-tested. All requirements from Claude Court Case #002 regarding UI hierarchy, CSV/Excel data ingestion, and NAAC accreditation claims softening can be achieved cleanly through targeted, minimal (/ponytail) modifications to `apps/api/static/index.html` and documentation, preserving 100% test passing across the test suite with zero regression risk.

---

## 5. Verification Method

1. **Automated Unit & API Tests**:
   - Run: `pytest`
   - Expected Output: 66/66 test cases passing with exit code 0 (`tests/api/test_naac_api.py`, `tests/unit/test_naac_domain.py`, etc.).
2. **Boot Check Validation**:
   - Run: `python scripts/boot_check.py`
   - Expected Output: `[BOOT_CHECK] All checks passed. System ready to boot.`
3. **UI Verification**:
   - Inspect `apps/api/static/index.html` to verify:
     - Topbar button displays `NAAC SSR Dossier (3.65)`.
     - Sidebar navigation places `action-list`, `student-reports`, `interventions-os`, and `ingestion-pipeline` front-and-center, while student practice tools are moved to secondary navigation.
     - Header of `#view-action-list` features the "Upload Dataset (CSV/Excel)" button.
     - `#view-naac-evaluator` displays "NAAC SSR Readiness & Evidence Dossier" with statutory disclaimer and metric validation.
