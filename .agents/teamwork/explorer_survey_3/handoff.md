# Handoff Report: Scoring Engine, ML Decoupling, Configurable Thresholds & Test Suite

**Agent**: Teamwork Explorer (`explorer_survey_3`)  
**Working Directory**: `c:\Users\priya\Desktop\Final_Hack\.agents\teamwork\explorer_survey_3`  
**Reference Document**: `c:\Users\priya\Desktop\Final_Hack\.agents\teamwork\explorer_survey_3\survey_report.md`  
**Date**: November 3, 2026  
**Type**: Hard Handoff (Investigation & Architecture Survey Complete)

---

## 1. Observation

1. **Test Suite Discovery & Execution**:
   - Location: 66 tests in `tests/` across 14 modules, and 14 tests in `test-report/regression-tests/test_ponytail_regressions.py`. Total = 80 tests.
   - Command executed:
     ```powershell
     .\.venv_win\Scripts\python.exe -m pytest tests test-report\regression-tests
     ```
   - Verbatim result:
     ```text
     ======================= 80 passed, 2 warnings in 5.24s ========================
     ```
   - `pyproject.toml:57` specifies `testpaths = ["tests"]`, meaning default `pytest` collects 66 items unless the regression path is included.
2. **Deterministic Scoring Core**:
   - `packages/domain/scores.py` implements pure AST arithmetic calculations with zero I/O imports:
     * Academic: `(cgpa * 10.0) - (3.0 * min(max(0, backlogs), 5))` (lines 50–55)
     * Attendance: `mean_attendance - (5.0 * max(0, subjects_below_60))` (lines 58–63)
     * Placement: `0.35 * aptitude + 0.40 * coding + 0.25 * mock` (lines 66–83)
     * Success score: `0.25*academic + 0.20*attendance + 0.20*placement + 0.15*lms + 0.10*engagement + 0.10*skills` (lines 160–188)
     * Tier classification: Safety hard floor -> Review band -> Score bands (lines 219–258)
     * Momentum: 3-week EWMA annotated as UP/DOWN/STABLE (ORDER ONLY, lines 191–216)
   - AST purity enforced in `tests/unit/test_ai_execution_contract.py:102–116`.
   - Determinism confirmed byte-identical in `tests/unit/test_determinism.py:12–52`.
   - Score decomposition provided at `GET /api/v1/students/{ref}/explain` (`apps/api/main.py:647–709`).
3. **Machine Learning Layer Positioning**:
   - Machine learning is implemented in `services/enrichment/ml_layer.py`.
   - `MODEL_CARD.md:8–9` declares: *"Default status: Disabled. Deterministic rules in the domain layer hold primary authority. Scoring path separation: The model does not write to tier, priority, segment, or score. It only records confidence_note and ml_agreement_boolean."*
   - In `services/pipeline.py:230`, pipeline writes static `confidence="High"` without invoking ML.
   - In `apps/api/static/index.html:3051`, navigation displays `AI Risk & Fairness Insights` with badge `94.2% Acc` under "Success Intelligence", and lines 5269–5335 display "Available AI Models" and "Interactive AI Risk Estimator", which Court Case #002 identified as creating buyer confusion.
4. **The 57% Emergency Hard Floor & 75% Standard Alert**:
   - `config/config.yaml:17`: `attendance_min: 57.0 # Below 57%: chronic absenteeism — cannot be coached out quickly`
   - `packages/domain/scores.py:235`: `floors or {"attendance_min": 57.0, "cgpa_min": 4.7, "backlog_max": 3}`
   - `config/rules.yaml:17`: `attendance_min: 75.0 # Only fires for students who ARE physically present`
   - There are currently no dynamic API endpoints or UI components to update or configure alert thresholds.

---

## 2. Logic Chain

1. **From Observation 1**: The monorepo has 80 passing tests that must remain passing without regressions. Any modification must not alter core contract interfaces, AST purity, or config integrity.
2. **From Observation 2 & 3**: Core scoring is already 100% deterministic arithmetic. The tension raised in Claude Court Case #002 ("You sell deterministic, no black box, but also ship ML dropout prediction... which one is it?") is an interface positioning problem, not an engine defect. Because the backend already adheres to Guardrails G1–G8, repositioning the UI and API metadata to frame ML strictly as an "Audited Fairness Proxy Add-on" resolves the tension completely without requiring architectural rewrites.
3. **From Observation 4**: In a 15-week academic semester, 57% attendance at week 9 (60% milestone) mathematically guarantees that even 100% attendance for the remaining 40% will yield only $0.60 \times 57\% + 0.40 \times 100\% = 74.2\% < 75.0\%$. Therefore, 57% is justifiable as an emergency hard floor (circuit-breaker). At the same time, standard university policy requires an alert at 75%. Introducing a configurable threshold overlay defaulting standard alert to 75% and emergency floor to 57% satisfies both institutional compliance and mathematical validity.

---

## 3. Caveats

1. **Config Hash Recalculation**: If `config/config.yaml` is modified directly on disk, its SHA-256 hash changes from `c4520cb10d798f6b`, which is referenced in static HTML fallbacks and `repository.py`. Therefore, dynamic threshold overrides should be applied via a lightweight in-memory/API overlay rather than directly overwriting `config.yaml` on disk, preserving boot check integrity.
2. **External System Integration**: Synthetic datasets were evaluated; live ERP integration was not tested.

---

## 4. Conclusion

1. **Test Suite**: All 80 pytest tests pass. Adding `"test-report/regression-tests"` to `pyproject.toml` enables single-command execution.
2. **Deterministic Core**: Scoring in `packages/domain/scores.py` is pure, explainable, and validated by AST inspection and determinism tests.
3. **ML Decoupling**: Reposition ML in UI (`apps/api/static/index.html`) from active risk engine to "Audited Fairness Proxy (Optional Add-on)" to eliminate positioning conflict while retaining fairness audit capabilities.
4. **57% Hard Floor**: Document the Week 9 point-of-no-return mathematical derivation ($74.2\% < 75\%$) in `STUDENT_SUCCESS_SCORE.md`, `README.md`, and frontend tooltips.
5. **Configurable Thresholds**: Implement `GET`/`PUT` endpoints for thresholds defaulting standard attendance warning to 75.0% and emergency floor to 57.0%.

---

## 5. Verification Method

1. **Verify 80 Existing Tests Pass**:
   ```powershell
   .\.venv_win\Scripts\python.exe -m pytest tests test-report\regression-tests
   ```
   *Expected outcome*: `80 passed in < 6.00s`.
2. **Verify AST Purity**:
   ```powershell
   .\.venv_win\Scripts\python.exe -m pytest tests/unit/test_ai_execution_contract.py
   ```
   *Expected outcome*: `1 passed` (confirms scoring files contain zero prohibited I/O or LLM calls).
3. **Verify Scoring Determinism**:
   ```powershell
   .\.venv_win\Scripts\python.exe -m pytest tests/unit/test_determinism.py
   ```
   *Expected outcome*: `2 passed` (confirms byte-identical output across repeated executions).
4. **Inspect Detailed Survey Report**:
   Read `c:\Users\priya\Desktop\Final_Hack\.agents\teamwork\explorer_survey_3\survey_report.md`.
