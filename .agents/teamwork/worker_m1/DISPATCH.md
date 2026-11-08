## 2026-11-03T05:03:22Z
You are teamwork_worker for Milestone 1. Your working directory is c:\Users\priya\Desktop\Final_Hack\.agents\teamwork\worker_m1.

MANDATORY FIRST STEP:
Read c:\Users\priya\Desktop\Final_Hack\.agents\teamwork\ORIGINAL_REQUEST.md before starting work.

ADDITIONAL REFERENCES:
Read c:\Users\priya\Desktop\Final_Hack\PROJECT.md
Read c:\Users\priya\Desktop\Final_Hack\.agents\teamwork\explorer_survey_3\survey_report.md
Read c:\Users\priya\Desktop\Final_Hack\.agents\teamwork\spec_miner_survey_1\survey_report.md
Read ponytail skill: c:\Users\priya\Desktop\Final_Hack\.agents\skills\ponytail\SKILL.md (keep changes minimal, focused, elegant)

EXCLUSIVE FILE WRITE OWNERSHIP:
- apps/api/main.py
- STUDENT_SUCCESS_SCORE.md
- README.md
Do NOT modify other code files. Do NOT modify config/config.yaml on disk (preserves boot hash).

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

STRICT CONSTRAINTS:
- DO NOT EXECUTE GIT PUSH. All changes remain strictly local.
- Zero regressions: all 80 existing pytest tests must pass.

YOUR ASSIGNMENT (Milestone 1: Backend Configurable Thresholds & ML Fairness Proxy API):
1. In `apps/api/main.py`:
   - Implement `GET /api/v1/config/thresholds` and `PUT /api/v1/config/thresholds` with Pydantic models.
   - Maintain a runtime/in-memory threshold overlay initialized from defaults:
     * `attendance_standard_min`: 75.0 (UGC/AICTE institutional standard)
     * `attendance_emergency_min`: 57.0 (emergency hard-floor)
     * `cgpa_warning_min`: 6.0
     * `cgpa_emergency_min`: 4.7
     * `backlog_warning_max`: 2
     * `backlog_emergency_max`: 3
     * `institutional_policy_default`: "UGC/AICTE 75% Standard"
     * `emergency_floor_rationale`: "Week 9 point of mathematical impossibility (0.60 * 57% + 0.40 * 100% = 74.2% < 75%)"
   - Validate on PUT: `attendance_emergency_min < attendance_standard_min`, `cgpa_emergency_min < cgpa_warning_min`, values in bounds.
   - Ensure the threshold API integrates cleanly with advisor triage and metadata endpoints.
   - Clarify ML endpoint tags/summaries in `apps/api/main.py` that ML operates strictly as an optional audited fairness proxy add-on.
2. In `STUDENT_SUCCESS_SCORE.md` and `README.md`:
   - Provide the explicit mathematical and pedagogical derivation of the 57% emergency hard-floor: In a 15-week term, Week 9 marks 60% completion. A student at 57% attendance at Week 9 achieves at most 74.2% final attendance even with 100% perfect attendance for the remaining 6 weeks (0.60 * 57% + 0.40 * 100% = 74.2% < 75.0%), making statutory 75% exam eligibility mathematically impossible without condonation.
   - Detail the configurable 75% standard attendance alert rule.
3. Verification:
   - Run `.\.venv_win\Scripts\python.exe -m pytest tests test-report\regression-tests` and verify all 80 tests pass.
   - Run `python scripts/boot_check.py` and verify all checks pass.
4. Report results in `handoff.md` and send a completion message with verification commands and output.
