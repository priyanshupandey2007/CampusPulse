# -*- coding: utf-8 -*-
"""
Unit and integration tests verifying all Claude Court Case #002 fixes:
- Configurable Alert Thresholds API & Invariant Validations (R3)
- Runtime Thresholds Integration & 100% Deterministic AST Explainability (R2, R3)
- Multi-format Ingestion Validation, Role Gate & 15MB Size Limit (R4)
- Zero-Regression NAAC A++ Grade Contract & SSR Rebranding (R4)
- Frontend Navigation Hierarchy, Secondary Student Labs & Ingestion Hero (R1, R4)
"""

import io
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from apps.api.main import app
from adapters.postgres.repository import get_db, Student
from packages.domain.naac import compute_live_naac_score

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_thresholds_around_test():
    """Ensure in-memory runtime threshold overlay is clean before and after every test."""
    client.post("/api/v1/config/thresholds/reset")
    yield
    client.post("/api/v1/config/thresholds/reset")


# ==============================================================================
# a. Thresholds API Tests (R3)
# ==============================================================================

def test_get_thresholds_returns_statutory_defaults_and_rationale():
    """
    Verify GET /api/v1/config/thresholds returns canonical UGC/AICTE 75% standard,
    57% emergency hard-floor, and Week 9 mathematical impossibility derivation.
    """
    response = client.get("/api/v1/config/thresholds")
    assert response.status_code == 200
    data = response.json()

    assert data["attendance_standard_min"] == 75.0
    assert data["attendance_emergency_min"] == 57.0
    assert data["cgpa_warning_min"] == 6.0
    assert data["cgpa_emergency_min"] == 4.7
    assert data["backlog_warning_max"] == 2
    assert data["backlog_emergency_max"] == 3
    assert data["institutional_policy_default"] == "UGC/AICTE 75% Standard"
    assert "Week 9 point of mathematical impossibility" in data["emergency_floor_rationale"]
    assert "0.60 * 57% + 0.40 * 100% = 74.2% < 75%" in data["emergency_floor_rationale"]


def test_put_thresholds_successfully_updates_valid_values():
    """Verify PUT /api/v1/config/thresholds successfully updates valid configurable thresholds."""
    update_payload = {
        "attendance_standard_min": 80.0,
        "attendance_emergency_min": 60.0,
        "cgpa_warning_min": 6.5,
        "cgpa_emergency_min": 5.0,
    }
    response = client.put("/api/v1/config/thresholds", json=update_payload)
    assert response.status_code == 200
    res_json = response.json()

    assert res_json["status"] == "updated"
    assert res_json["thresholds"]["attendance_standard_min"] == 80.0
    assert res_json["thresholds"]["attendance_emergency_min"] == 60.0
    assert res_json["thresholds"]["cgpa_warning_min"] == 6.5
    assert res_json["thresholds"]["cgpa_emergency_min"] == 5.0

    # Confirm persistence in subsequent GET call
    get_res = client.get("/api/v1/config/thresholds")
    assert get_res.status_code == 200
    assert get_res.json()["attendance_standard_min"] == 80.0
    assert get_res.json()["attendance_emergency_min"] == 60.0


def test_put_thresholds_returns_422_when_emergency_attendance_gte_standard():
    """
    Verify PUT /api/v1/config/thresholds returns HTTP 422 VALIDATION_ERROR
    when attendance_emergency_min >= attendance_standard_min.
    """
    # Case 1: emergency attendance equal to standard attendance
    res_equal = client.put(
        "/api/v1/config/thresholds",
        json={"attendance_emergency_min": 75.0},
    )
    assert res_equal.status_code == 422
    body_equal = res_equal.json()
    assert body_equal["error"]["code"] == "VALIDATION_ERROR"
    assert "attendance_emergency_min" in body_equal["error"]["hint"]

    # Case 2: emergency attendance strictly greater than standard attendance
    res_greater = client.put(
        "/api/v1/config/thresholds",
        json={"attendance_emergency_min": 85.0, "attendance_standard_min": 70.0},
    )
    assert res_greater.status_code == 422
    body_greater = res_greater.json()
    assert body_greater["error"]["code"] == "VALIDATION_ERROR"
    assert "strictly less than attendance_standard_min" in body_greater["error"]["hint"]


def test_put_thresholds_returns_422_when_cgpa_emergency_gte_warning():
    """
    Verify PUT /api/v1/config/thresholds returns HTTP 422 VALIDATION_ERROR
    when cgpa_emergency_min >= cgpa_warning_min.
    """
    # Case 1: emergency CGPA equal to warning CGPA (default warning is 6.0)
    res_equal = client.put(
        "/api/v1/config/thresholds",
        json={"cgpa_emergency_min": 6.0},
    )
    assert res_equal.status_code == 422
    body_equal = res_equal.json()
    assert body_equal["error"]["code"] == "VALIDATION_ERROR"
    assert "cgpa_emergency_min" in body_equal["error"]["hint"]

    # Case 2: emergency CGPA strictly greater than warning CGPA
    res_greater = client.put(
        "/api/v1/config/thresholds",
        json={"cgpa_emergency_min": 7.5, "cgpa_warning_min": 6.0},
    )
    assert res_greater.status_code == 422
    body_greater = res_greater.json()
    assert body_greater["error"]["code"] == "VALIDATION_ERROR"
    assert "strictly less than cgpa_warning_min" in body_greater["error"]["hint"]


def test_put_thresholds_rejects_out_of_bounds_values_with_422():
    """Verify PUT /api/v1/config/thresholds enforces Pydantic field bounds (0-100% attendance, 0-10 CGPA)."""
    # Attendance > 100%
    res_high_att = client.put("/api/v1/config/thresholds", json={"attendance_standard_min": 105.0})
    assert res_high_att.status_code == 422
    assert res_high_att.json()["error"]["code"] == "VALIDATION_ERROR"

    # Attendance < 0%
    res_neg_att = client.put("/api/v1/config/thresholds", json={"attendance_emergency_min": -5.0})
    assert res_neg_att.status_code == 422
    assert res_neg_att.json()["error"]["code"] == "VALIDATION_ERROR"

    # CGPA > 10.0
    res_high_cgpa = client.put("/api/v1/config/thresholds", json={"cgpa_warning_min": 11.0})
    assert res_high_cgpa.status_code == 422
    assert res_high_cgpa.json()["error"]["code"] == "VALIDATION_ERROR"


def test_post_thresholds_reset_restores_institutional_defaults():
    """Verify POST /api/v1/config/thresholds/reset resets all thresholds to canonical defaults."""
    # First modify thresholds
    client.put("/api/v1/config/thresholds", json={
        "attendance_standard_min": 85.0,
        "attendance_emergency_min": 65.0,
        "cgpa_warning_min": 7.0,
        "cgpa_emergency_min": 5.5,
    })

    # Execute reset
    reset_res = client.post("/api/v1/config/thresholds/reset")
    assert reset_res.status_code == 200
    res_data = reset_res.json()
    assert res_data["status"] == "reset"
    assert res_data["thresholds"]["attendance_standard_min"] == 75.0
    assert res_data["thresholds"]["attendance_emergency_min"] == 57.0
    assert res_data["thresholds"]["cgpa_warning_min"] == 6.0
    assert res_data["thresholds"]["cgpa_emergency_min"] == 4.7


# ==============================================================================
# b. Threshold Integration & Explainability Tests (R2, R3)
# ==============================================================================

def test_effective_config_includes_active_thresholds_and_overlaid_floors():
    """
    Verify GET /api/v1/config/effective reflects active runtime thresholds
    and overlays floors accordingly.
    """
    response = client.get("/api/v1/config/effective")
    assert response.status_code == 200
    data = response.json()["data"]

    assert "thresholds" in data
    assert data["thresholds"]["attendance_standard_min"] == 75.0
    assert data["thresholds"]["attendance_emergency_min"] == 57.0

    floors = data["floors"]
    assert floors["attendance_standard_min"] == 75.0
    assert floors["attendance_min"] == 57.0
    assert floors["cgpa_warning_min"] == 6.0
    assert floors["cgpa_min"] == 4.7

    # Update threshold and verify effective config dynamically updates
    client.put("/api/v1/config/thresholds", json={"attendance_standard_min": 78.0, "attendance_emergency_min": 58.0})
    updated_res = client.get("/api/v1/config/effective")
    updated_floors = updated_res.json()["data"]["floors"]
    assert updated_floors["attendance_standard_min"] == 78.0
    assert updated_floors["attendance_min"] == 58.0


def test_student_explain_endpoint_includes_deterministic_ast_and_ml_proxy_role():
    """
    Verify GET /api/v1/students/{ref}/explain contains explicit deterministic AST confirmation
    and audited fairness proxy role, along with active thresholds in the audit envelope.
    """
    db = next(get_db())
    student = db.query(Student).first()
    assert student is not None, "At least one student record must exist in test database"
    ref = student.student_ref

    response = client.get(
        f"/api/v1/students/{ref}/explain",
        headers={"X-User-Role": "advisor", "X-User-Email": "advisor@campuspulse.edu"},
    )
    assert response.status_code == 200
    data = response.json()["data"]

    assert "audit" in data
    audit = data["audit"]
    assert audit["scoring_engine"] == "100% deterministic AST"
    assert audit["ml_role"] == "audited_fairness_proxy_secondary"
    assert "thresholds" in audit
    assert audit["thresholds"]["attendance_standard_min"] == 75.0
    assert audit["thresholds"]["attendance_emergency_min"] == 57.0
    assert "contributions" in data and len(data["contributions"]) > 0


# ==============================================================================
# c. Ingestion & NAAC Tests (R4)
# ==============================================================================

def test_ingest_upload_rejects_invalid_file_formats():
    """Verify POST /api/v1/ingest/upload rejects unsupported file extensions with HTTP 400."""
    invalid_files = [
        ("malicious.exe", b"MZexecutable", "application/octet-stream"),
        ("exploit.php", b"<?php phpinfo(); ?>", "application/x-php"),
        ("script.sh", b"#!/bin/bash\necho 1", "application/x-sh"),
        ("document.pdf", b"%PDF-1.4...", "application/pdf"),
    ]
    for filename, content, mime in invalid_files:
        dummy_file = io.BytesIO(content)
        res = client.post(
            "/api/v1/ingest/upload",
            files={"file": (filename, dummy_file, mime)},
            headers={"X-User-Role": "admin", "X-User-Email": "admin@campuspulse.edu"},
        )
        assert res.status_code == 400
        json_data = res.json()
        assert "Invalid file extension" in json_data["error"]["message"]


def test_ingest_upload_enforces_15mb_file_size_limit():
    """Verify POST /api/v1/ingest/upload enforces 15MB file size limit with HTTP 413."""
    oversized_size = 15 * 1024 * 1024 + 1024  # 15 MB + 1 KB
    dummy_large_file = io.BytesIO(b"A" * oversized_size)

    res = client.post(
        "/api/v1/ingest/upload",
        files={"file": ("oversized_dataset.csv", dummy_large_file, "text/csv")},
        headers={"X-User-Role": "admin", "X-User-Email": "admin@campuspulse.edu"},
    )
    assert res.status_code == 413
    assert "File exceeds maximum allowed size of 15MB" in res.json()["error"]["message"]

    # Verify no leaked temporary files remain in data/raw
    for f in Path("./data/raw").glob("*oversized_dataset*"):
        try:
            f.unlink()
        except OSError:
            pass


def test_ingest_upload_forbids_student_role():
    """Verify POST /api/v1/ingest/upload rejects student role access with HTTP 403."""
    dummy_file = io.BytesIO(b"Roll Number,Name\n2023CSE001,Test\n")
    res = client.post(
        "/api/v1/ingest/upload",
        files={"file": ("dataset.csv", dummy_file, "text/csv")},
        headers={"X-User-Role": "student", "X-User-Email": "student@campuspulse.edu"},
    )
    assert res.status_code == 403
    assert "Students cannot upload or ingest institutional dataset files" in res.json()["error"]["message"]


def test_naac_calculation_grade_a_double_plus_zero_regression():
    """
    Verify NAAC evaluation continues to output grade == 'A++' across both
    pure domain function and API endpoints (zero regression contract).
    """
    # 1. Pure domain calculation check
    domain_result = compute_live_naac_score()
    assert domain_result["grade"] == "A++"
    assert 3.51 <= domain_result["cgpa"] <= 4.00
    assert domain_result["total_weight"] == 1000

    # 2. API overview endpoint check
    api_res = client.get("/api/v1/naac/overview")
    assert api_res.status_code == 200
    api_data = api_res.json()["data"]
    assert api_data["grade"] == "A++"
    assert api_data["cgpa"] >= 3.51


# ==============================================================================
# d. Frontend HTML Navigation & Rebranding Tests (R1, R2, R3, R4)
# ==============================================================================

def test_frontend_secondary_student_practice_labs():
    """Verify GET / de-emphasizes peripheral student tools to 'Student Practice Labs (Secondary)'."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.text

    assert "Student Practice Labs (Secondary)" in html
    assert "Early-Warning Triage" in html
    assert 'onclick="switchNav(\'action-list\')"' in html


def test_frontend_dominant_primary_ingestion_hero():
    """
    Verify GET / includes 'Upload Dataset (CSV/Excel)' in action list header
    and dominant CSV/Excel upload hero card in ingestion pipeline.
    """
    response = client.get("/")
    assert response.status_code == 200
    html = response.text

    assert "Upload Dataset (CSV/Excel)" in html
    assert "Upload Institution Dataset (CSV / Excel)" in html
    assert "Primary Onboarding Step 1" in html
    assert "Demonstration &amp; Evaluation Presets (Secondary)" in html


def test_frontend_naac_ssr_readiness_dossier_and_statutory_notice():
    """
    Verify GET / contains 'NAAC SSR Readiness & Evidence Dossier' and
    statutory metric validation notice softening marketing claims.
    """
    response = client.get("/")
    assert response.status_code == 200
    html = response.text

    assert "NAAC SSR Readiness &amp; Evidence Dossier" in html or "NAAC SSR Readiness & Evidence Dossier" in html
    assert "NAAC SSR Dossier (3.65)" in html
    assert "Statutory Metric Validation Notice" in html
    assert "Statutory accreditation grades and formal institutional ratings are determined exclusively by official NAAC peer-teams" in html


def test_frontend_week9_mathematical_impossibility_and_threshold_modal():
    """
    Verify GET / includes 'Week 9 point of mathematical impossibility'
    and configurable threshold modal container (#modal-thresholds).
    """
    response = client.get("/")
    assert response.status_code == 200
    html = response.text

    assert "Week 9 point of mathematical impossibility" in html
    assert "modal-thresholds" in html
    assert "thresh-att-std" in html
    assert "thresh-att-emg" in html
    assert "Audited Fairness Proxy (Optional Add-on)" in html
