## 2026-11-03T05:19:54Z
You are teamwork_worker for Milestone 2. Your working directory is c:\Users\priya\Desktop\Final_Hack\.agents\teamwork\worker_m2.

MANDATORY FIRST STEP:
Read c:\Users\priya\Desktop\Final_Hack\.agents\teamwork\ORIGINAL_REQUEST.md before starting work.

ADDITIONAL REFERENCES:
Read c:\Users\priya\Desktop\Final_Hack\PROJECT.md
Read c:\Users\priya\Desktop\Final_Hack\.agents\teamwork\explorer_survey_2\survey_report.md
Read c:\Users\priya\Desktop\Final_Hack\.agents\teamwork\spec_miner_survey_1\survey_report.md
Read c:\Users\priya\Desktop\Final_Hack\.agents\teamwork\worker_m1\handoff.md
Read ponytail skill: c:\Users\priya\Desktop\Final_Hack\.agents\skills\ponytail\SKILL.md (keep changes minimal, focused, elegant)

EXCLUSIVE FILE WRITE OWNERSHIP:
- apps/api/static/index.html
Do NOT modify other files.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

STRICT CONSTRAINTS:
- DO NOT EXECUTE GIT PUSH. All changes remain strictly local.
- Zero regressions: all 80 existing pytest tests must pass.

YOUR ASSIGNMENT (Milestone 2: Frontend Navigation Hierarchy, Ingestion Elevation & NAAC Rebranding):
In `apps/api/static/index.html`:
1. **Primary Navigation Hierarchy & Secondary Student Labs (R1)**:
   - Restructure sidebar navigation (`<nav class="sidebar-nav">`): Elevate advisor early-warning triage (`action-list`), student 360 profile (`student-reports`), intervention tracking (`interventions-os`), and data ingestion (`ingestion-pipeline`) to front-and-center.
   - Group peripheral student tools (`code-editor`, `lab-practice`, `ai-interviewer`, `ai-mentor`, `learn-modules`, `project-bank`) into a clearly designated secondary section titled `"Student Practice Labs (Secondary)"` or a collapsed/secondary drawer.
   - Preserve all existing DOM IDs (`#view-*`), `ROLE_METADATA`, and `switchNav` routes so that all existing views remain accessible and no Javascript breaks.
2. **Primary CSV/Excel Ingestion Hero (R4)**:
   - In `#view-action-list` header: Add a clear "Upload Dataset (CSV/Excel)" action button linking to `#view-ingestion-pipeline` (`switchNav('ingestion-pipeline')`).
   - In `#view-ingestion-pipeline`: Reorganize the cards so custom CSV/Excel upload is the dominant primary hero card and first onboarding step, positioned above or more prominently than demo presets.
3. **Configurable Alert Thresholds UI (R3)**:
   - In `#view-action-list` (or in institutional settings): Add a threshold config modal or inline banner reflecting `GET /api/v1/config/thresholds` and allowing `PUT /api/v1/config/thresholds` updates.
   - Default standard attendance alert to 75% (institutional UGC/AICTE standard) and emergency floor to 57%.
   - Include tooltip/explanation for 57% emergency hard-floor: "Week 9 point of mathematical impossibility (0.60 * 57% + 0.40 * 100% = 74.2% < 75%)".
4. **Machine Learning Repositioning (R2)**:
   - Rebrand ML in sidebar nav and views from active risk predictor to `"Audited Fairness Proxy (Optional Add-on)"`.
   - Update view copy to explain that student success scoring is 100% deterministic pure AST arithmetic, and ML operates strictly as an optional audited fairness proxy add-on for demographic parity and disagreement audits.
5. **Accreditation Claims Softening (R4)**:
   - Rebrand all marketing copy and badges from "NAAC A++ forecasting" to `"NAAC SSR Readiness & Evidence Dossier"`.
   - Update topbar button text to `"NAAC SSR Dossier (3.65)"`.
   - In `#view-naac-evaluator`: Update title to "NAAC SSR Readiness & Evidence Dossier", and add statutory metric validation disclaimers clarifying that statutory accreditation is determined exclusively by official NAAC peer-teams.
   - DO NOT alter backend dictionary keys or break tests.
6. Verification:
   - Run `.\.venv_win\Scripts\python.exe -m pytest tests test-report\regression-tests` and verify all 80 tests pass.
   - Run `python scripts/boot_check.py` and verify all checks pass.
7. Report results in `handoff.md` and send a completion message with verification commands and output.
