# Milestone 1 Handoff Report: Backend Configurable Thresholds & ML Fairness Proxy API

**Agent**: `worker_m1`  
**Milestone**: Milestone 1 (Backend Configurable Thresholds & ML Fairness Proxy API)  
**Target Files**: `apps/api/main.py`, `STUDENT_SUCCESS_SCORE.md`, `README.md`  
**Timestamp**: 2026-11-03T05:19:00Z  

---

## 1. Observation

1. **Baseline Invariants Verified**:
   - `.\.venv_win\Scripts\python.exe -m pytest tests test-report\regression-tests` passed with exactly `80 passed, 2 warnings in 5.08s`.
   - `python scripts/boot_check.py` exited with code 0: `config_hash = c4520cb10d798f6b`, `targets_hash = d5b6b2c7c6b38c79`, and `weights sum = 1.0000000000`.
   - Disk configuration in `config/config.yaml` was untouched, preserving startup cryptographic hash integrity.
2. **Endpoint Implementations & Integration in `apps/api/main.py`**:
   - Lines 442–540: Defined `DEFAULT_THRESHOLDS` and `RUNTIME_THRESHOLDS` in-memory overlay initialized to:
     * `attendance_standard_min`: 75.0 (UGC/AICTE institutional standard)
     * `attendance_emergency_min`: 57.0 (emergency hard-floor)
     * `cgpa_warning_min`: 6.0
     * `cgpa_emergency_min`: 4.7
     * `backlog_warning_max`: 2
     * `backlog_emergency_max`: 3
     * `institutional_policy_default`: "UGC/AICTE 75% Standard"
     * `emergency_floor_rationale`: "Week 9 point of mathematical impossibility (0.60 * 57% + 0.40 * 100% = 74.2% < 75%)"
   - Defined Pydantic models `ThresholdConfigResponse` and `ThresholdUpdateRequest` with `model_validator(mode="after")` enforcing bounds and strict relationship requirements (`attendance_emergency_min < attendance_standard_min` and `cgpa_emergency_min < cgpa_warning_min`).
   - Implemented `GET /api/v1/config/thresholds`, `PUT /api/v1/config/thresholds`, and `POST /api/v1/config/thresholds/reset`.
   - Integrated threshold overlay into:
     * `GET /api/v1/config/effective`: overlays `floors` and attaches `"thresholds": dict(RUNTIME_THRESHOLDS)`.
     * `GET /api/v1/advisors/me/action-list`: attaches `"standard_attendance_alert"` and `"emergency_hard_floor_breach"` flags per student action item, and returns active `"thresholds"`.
     * `GET /api/v1/students/{student_ref}/explain`: includes active `"thresholds"`, `"scoring_engine": "100% deterministic AST"`, and `"ml_role": "audited_fairness_proxy_secondary"` in audit envelope.
   - Clarified ML endpoints (`/health/ml`, `/api/v1/ml/status`, `/api/v1/ml/models`, `/api/v1/ml/feature-importance`, `/api/v1/ml/evaluation`, `/api/v1/ml/predict-risk`, `/api/v1/ml/agreement-check`):
     * Added `tags=["Optional Audited Fairness Proxy"]`
     * Updated summaries and docstrings explicitly confirming that core student scoring is 100% deterministic pure AST arithmetic and ML serves strictly as an optional audited fairness proxy add-on.
3. **Documentation Enhancements**:
   - `STUDENT_SUCCESS_SCORE.md`: Documented Section 3 with the two-tier framework table, formal mathematical derivation of the 57% emergency hard-floor ($0.60 \times 57\% + 0.40 \times 100\% = 74.2\% < 75.0\%$, making statutory 75% exam eligibility mathematically impossible without condonation), configurable 75% standard attendance alert rule, and tier classification precedence.
   - `README.md`: Documented the two-tier alert architecture, 57% mathematical derivation, configurable thresholds API endpoints, and repositioned ML as an optional audited fairness proxy add-on under Guardrails G1-G8.

---

## 2. Logic Chain

1. **Precedence**: Claude Court Case #002 identified tension between claims of "100% deterministic early warning" and UI/API presentations of "94.2% accuracy ML risk models", along with an unjustified 57% hard-floor cutoff that seemed to conflict with standard 75% university policies.
2. **Resolution Mechanism**:
   - The 75% attendance rule is the standard institutional alert threshold (under UGC/AICTE statutory mandates), while the 57% threshold is a safety circuit-breaker marking the mathematical point of impossibility at Week 9 (60% completion of a 15-week term).
   - Keeping the runtime overlay in memory in `apps/api/main.py` preserves `config/config.yaml` on disk, guaranteeing that `boot_check.py` continues to verify the identical canonical SHA-256 boot hash `c4520cb10d798f6b`.
   - Using Pydantic models with `@model_validator(mode="after")` ensures invalid relationship updates (such as setting the emergency floor above the standard alert) throw 422 `VALIDATION_ERROR` seamlessly handled by FastAPI's existing error envelope handler.
   - Annotating OpenAPI tags and summaries across `/api/v1/ml/*` endpoints legally and architecturally solidifies that the core scoring is 100% deterministic AST arithmetic and ML is an optional, audited fairness proxy add-on.

---

## 3. Caveats

- **Runtime In-Memory Persistence**: Threshold modifications via `PUT /api/v1/config/thresholds` are held in process memory (`RUNTIME_THRESHOLDS`) so as to preserve the file-system boot hash of `config/config.yaml`. Restarting the web process resets thresholds to canonical institutional defaults (75% standard, 57% emergency floor).
- **No Git Push**: In accordance with the project constraints, no git push commands were executed; all changes remain strictly local.

---

## 4. Conclusion

Milestone 1 is complete:
- Configurable thresholds API (`GET`/`PUT`/`POST reset`) is implemented and verified.
- The 57% emergency hard-floor is mathematically and pedagogically derived and documented in both `STUDENT_SUCCESS_SCORE.md` and `README.md`.
- The 75% UGC/AICTE standard attendance alert rule is established as the default configurable policy.
- ML endpoints and metadata are explicitly repositioned as an optional audited fairness proxy add-on without touching the deterministic scoring core.
- All 80 existing pytest tests pass with zero regressions.

---

## 5. Verification Method

To independently verify the Milestone 1 deliverables:

```powershell
# 1. Run all 80 existing pytest tests (must pass with 0 failures)
.\.venv_win\Scripts\python.exe -m pytest tests test-report\regression-tests

# 2. Run the startup boot validation (must verify hashes and weights)
.\.venv_win\Scripts\python.exe scripts/boot_check.py

# 3. Test the configurable threshold API endpoints and validation checks
.\.venv_win\Scripts\python.exe -c "
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)

# GET thresholds check
res_get = client.get('/api/v1/config/thresholds')
assert res_get.status_code == 200
data = res_get.json()
assert data['attendance_standard_min'] == 75.0
assert data['attendance_emergency_min'] == 57.0
assert data['cgpa_warning_min'] == 6.0
assert data['cgpa_emergency_min'] == 4.7

# PUT valid check
res_put = client.put('/api/v1/config/thresholds', json={'attendance_standard_min': 80.0, 'attendance_emergency_min': 60.0})
assert res_put.status_code == 200
assert res_put.json()['thresholds']['attendance_standard_min'] == 80.0

# PUT invalid relationship check (422)
res_inv = client.put('/api/v1/config/thresholds', json={'attendance_emergency_min': 85.0})
assert res_inv.status_code == 422
assert res_inv.json()['error']['code'] == 'VALIDATION_ERROR'

# Reset to defaults
res_reset = client.post('/api/v1/config/thresholds/reset')
assert res_reset.status_code == 200
assert res_reset.json()['thresholds']['attendance_standard_min'] == 75.0

print('Milestone 1 Verification PASSED!')
"
```
