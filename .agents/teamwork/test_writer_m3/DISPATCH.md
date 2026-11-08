## 2026-11-03T05:43:07Z

You are teamwork_test_writer for Milestone 3. Your working directory is c:\Users\priya\Desktop\Final_Hack\.agents\teamwork\test_writer_m3.

MANDATORY FIRST STEP:
Read c:\Users\priya\Desktop\Final_Hack\.agents\teamwork\ORIGINAL_REQUEST.md before starting work.

ADDITIONAL REFERENCES:
Read c:\Users\priya\Desktop\Final_Hack\PROJECT.md
Read c:\Users\priya\Desktop\Final_Hack\.agents\teamwork\worker_m1\handoff.md
Read c:\Users\priya\Desktop\Final_Hack\.agents\teamwork\worker_m2\handoff.md
Read ponytail skill: c:\Users\priya\Desktop\Final_Hack\.agents\skills\ponytail\SKILL.md (keep changes minimal, focused, elegant)

EXCLUSIVE FILE WRITE OWNERSHIP:
- pyproject.toml
- tests/unit/test_court_case_fixes.py
Do NOT modify other files.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

STRICT CONSTRAINTS:
- DO NOT EXECUTE GIT PUSH. All changes remain strictly local.
- Zero regressions: all 80 existing pytest tests must pass, and all new tests must pass.

YOUR ASSIGNMENT (Milestone 3: Test Suite Expansion & Pyproject Configuration):
1. In `pyproject.toml`:
   - Update `testpaths` to include `"test-report/regression-tests"`:
     `testpaths = ["tests", "test-report/regression-tests"]`
     so that running standard `pytest` executes all 80 existing tests without extra flags.
2. In `tests/unit/test_court_case_fixes.py`:
   - Write comprehensive unit tests verifying all Court Case #002 fixes:
     a. **Thresholds API Tests**:
        - `GET /api/v1/config/thresholds` returns default 75.0% standard attendance, 57.0% emergency attendance, and mathematical rationale.
        - `PUT /api/v1/config/thresholds` successfully updates valid thresholds.
        - `PUT /api/v1/config/thresholds` returns HTTP 422 `VALIDATION_ERROR` when `attendance_emergency_min >= attendance_standard_min` or `cgpa_emergency_min >= cgpa_warning_min`.
        - `POST /api/v1/config/thresholds/reset` resets to canonical institutional defaults.
     b. **Threshold Integration & Explainability Tests**:
        - `GET /api/v1/config/effective` includes active thresholds.
        - `GET /api/v1/students/{ref}/explain` includes deterministic AST confirmation and audited fairness proxy role.
     c. **Ingestion & NAAC Tests**:
        - CSV/Excel upload endpoint `/api/v1/ingest/upload` rejects invalid formats and enforces 15MB limit.
        - NAAC calculation continues to output `grade == "A++"` (zero regression contract).
     d. **Frontend HTML Navigation & Rebranding Tests**:
        - `GET /` contains "Student Practice Labs (Secondary)".
        - `GET /` contains "Upload Dataset (CSV/Excel)" and dominant primary ingestion hero.
        - `GET /` contains "NAAC SSR Readiness & Evidence Dossier" and statutory metric validation notice.
        - `GET /` contains "Week 9 point of mathematical impossibility".
3. Run tests:
   - Run `.\.venv_win\Scripts\python.exe -m pytest` and verify all tests (80 existing + new tests) pass with zero failures.
   - Run `python scripts/boot_check.py` and verify boot check passes.
4. Report results in `handoff.md` and send completion message with verification commands and output.
