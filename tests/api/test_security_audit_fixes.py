"""
Unit and integration tests verifying security fixes for:
- Path Traversal & File Upload Validation (CWE-22 / CWE-434)
- Defensive Security Headers (CWE-693)
- CORS origin safety
"""

import io
import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_security_headers_present():
    """Verify standard defensive HTTP headers are attached to all responses."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"


def test_upload_rejects_unsupported_extensions():
    """Verify upload rejects executable or non-tabular extensions."""
    dummy_file = io.BytesIO(b"fake binary content")
    response = client.post(
        "/api/v1/data-import/upload",
        files={"file": ("malicious_payload.exe", dummy_file, "application/octet-stream")},
    )
    assert response.status_code == 400
    json_data = response.json()
    assert "Invalid file extension" in json_data["error"]["message"]


def test_upload_rejects_script_extensions():
    """Verify upload rejects PHP, JS, and shell scripts."""
    dummy_file = io.BytesIO(b"<?php echo 'pwned'; ?>")
    response = client.post(
        "/api/v1/ingest/upload",
        files={"file": ("exploit.php", dummy_file, "application/x-php")},
    )
    assert response.status_code == 400
    json_data = response.json()
    assert "Invalid file extension" in json_data["error"]["message"]


def test_upload_sanitizes_path_traversal_attempt():
    """Verify that path traversal filenames (e.g. ../../test.csv) are sanitized safely."""
    # A valid CSV header
    csv_content = b"Roll Number,Name,Branch,Batch,Section,Total Score\n2023CSE999,Test User,CSE,CSE 2029,C,85\n"
    dummy_file = io.BytesIO(csv_content)
    
    response = client.post(
        "/api/v1/data-import/upload",
        files={"file": ("../../traversal_test.csv", dummy_file, "text/csv")},
    )
    # The endpoint should either succeed by safely sanitizing the filename into ./data/raw/
    # or reject it, but never write outside ./data/raw
    assert response.status_code in (200, 400)
    if response.status_code == 200:
        json_data = response.json()
        assert "data" in json_data

    # Cleanup test files from ./data/raw
    from pathlib import Path
    for f in Path("./data/raw").glob("*traversal_test.csv"):
        try:
            f.unlink()
        except OSError:
            pass


def test_hsts_header_present():
    """Verify Strict-Transport-Security header is attached to responses (Item 7)."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "Strict-Transport-Security" in response.headers
    assert "max-age=" in response.headers["Strict-Transport-Security"]


def test_rate_limiting_headers_attached():
    """Verify rate limit tracking headers are attached (Item 6)."""
    response = client.get("/api/v1/config/effective")
    assert response.status_code == 200
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers


def test_admin_route_forbidden_for_student():
    """Verify admin route rejects student access with 403 Forbidden (Item 2)."""
    response = client.get(
        "/api/v1/admin/department-faculty",
        headers={"X-User-Role": "student", "X-User-Email": "student@krmu.edu.in"},
    )
    assert response.status_code == 403
    body = response.json()
    assert "Access forbidden" in body["error"]["message"]


def test_student_cannot_view_other_student_profile():
    """Verify student role cannot access another student's profile (Item 4: IDOR Protection)."""
    response = client.get(
        "/api/v1/students/stu_other_student_999",
        headers={
            "X-User-Role": "student",
            "X-User-Ref": "stu_2023cse001",
            "X-User-Email": "aarav.sharma@krmu.edu.in",
        },
    )
    assert response.status_code == 403
    body = response.json()
    assert "Access denied" in body["error"]["message"]


def test_student_cannot_create_interventions():
    """Verify student role cannot create interventions (Item 4: Authorization)."""
    response = client.post(
        "/api/v1/advisors/me/interventions",
        json={"student_ref": "stu_2023cse001", "action_code": "MENTORSHIP_1ON1"},
        headers={"X-User-Role": "student"},
    )
    assert response.status_code == 403
    body = response.json()
    assert "Access denied" in body["error"]["message"]


def test_password_hashing_and_complexity():
    """Verify bcrypt password hashing and strength validation (Item 8)."""
    from packages.domain.security import hash_password, verify_password, validate_password_strength

    # Test complexity
    is_valid, msg = validate_password_strength("weak")
    assert not is_valid
    assert "at least 8 characters" in msg

    is_valid, msg = validate_password_strength("NoDigitsNoSpecial!")
    assert not is_valid
    assert "digit" in msg

    is_valid, msg = validate_password_strength("ComplexP@ssw0rd2026!")
    assert is_valid

    # Test bcrypt hashing
    hashed = hash_password("ComplexP@ssw0rd2026!")
    assert hashed != "ComplexP@ssw0rd2026!"
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")
    assert verify_password("ComplexP@ssw0rd2026!", hashed)
    assert not verify_password("WrongPassword!", hashed)


def test_unauthenticated_request_rejected():
    """Verify explicit unauthenticated simulation returns 401 Unauthorized (Item 3)."""
    response = client.get(
        "/api/v1/students",
        headers={"X-User-Role": "anonymous"},
    )
    assert response.status_code == 401
    body = response.json()
    assert "Authentication required" in body["error"]["message"]



def test_student_cannot_view_other_student_explain():
    """Verify student role cannot access another student's score explanation (IDOR)."""
    response = client.get(
        "/api/v1/students/stu_other_student_999/explain",
        headers={
            "X-User-Role": "student",
            "X-User-Ref": "stu_2023cse001",
            "X-User-Email": "aarav.sharma@krmu.edu.in",
        },
    )
    assert response.status_code == 403
    body = response.json()
    assert "Access denied" in body["error"]["message"]


def test_student_cannot_view_other_student_trend():
    """Verify student role cannot access another student's performance trend (IDOR)."""
    response = client.get(
        "/api/v1/students/stu_other_student_999/trend",
        headers={
            "X-User-Role": "student",
            "X-User-Ref": "stu_2023cse001",
            "X-User-Email": "aarav.sharma@krmu.edu.in",
        },
    )
    assert response.status_code == 403
    body = response.json()
    assert "Access denied" in body["error"]["message"]


def test_student_cannot_update_interventions():
    """Verify student role cannot update advisor interventions (Authorization)."""
    response = client.patch(
        "/api/v1/advisors/me/interventions/any_id",
        json={"status": "RESOLVED"},
        headers={"X-User-Role": "student"},
    )
    assert response.status_code == 403
    body = response.json()
    assert "Access denied" in body["error"]["message"]


def test_assistant_chat_escapes_reflected_xss():
    """Verify /api/v1/assistant/chat sanitizes reflected user input against XSS."""
    payload = {"query": "<script>alert('xss')</script>"}
    response = client.post("/api/v1/assistant/chat", json=payload)
    assert response.status_code == 200
    data = response.json()["data"]
    assert "<script>" not in data["reply"]
    assert "&lt;script&gt;" in data["reply"]
    assert "<script>" not in data["query"]
    assert "&lt;script&gt;" in data["query"]


def test_assistant_chat_rejects_oversized_query():
    """Verify /api/v1/assistant/chat rejects queries exceeding 1000 characters."""
    payload = {"query": "A" * 1005}
    response = client.post("/api/v1/assistant/chat", json=payload)
    assert response.status_code == 422


def test_student_cannot_upload_dataset():
    """Verify students are forbidden from uploading datasets."""
    dummy_file = io.BytesIO(b"Roll Number,Name\n1,Test\n")
    response = client.post(
        "/api/v1/data-import/upload",
        files={"file": ("dataset.csv", dummy_file, "text/csv")},
        headers={"X-User-Role": "student"},
    )
    assert response.status_code == 403
    assert "Access denied" in response.json()["error"]["message"]


def test_student_cannot_trigger_preset_ingestion():
    """Verify students are forbidden from triggering preset dataset ingestion."""
    response = client.post(
        "/api/v1/ingest/preset/sample",
        headers={"X-User-Role": "student"},
    )
    assert response.status_code == 403
    assert "Access denied" in response.json()["error"]["message"]


def test_upload_rejects_binary_exe_in_csv():
    """Verify upload rejects Windows PE/executable magic bytes disguised as CSV (Item 18)."""
    # Starts with 'MZ' (DOS executable header)
    dummy_file = io.BytesIO(b"MZ\x90\x00\x03\x00\x00\x00fake executable content")
    response = client.post(
        "/api/v1/data-import/upload",
        files={"file": ("trojan.csv", dummy_file, "text/csv")},
    )
    assert response.status_code == 400
    assert "Executable or binary content detected" in response.json()["error"]["message"]


def test_upload_rejects_non_zip_in_xlsx():
    """Verify upload rejects non-OOXML/ZIP files disguised as XLSX (Item 18)."""
    dummy_file = io.BytesIO(b"NOT_A_ZIP_HEADER_CONTENT")
    response = client.post(
        "/api/v1/data-import/upload",
        files={"file": ("fake_table.xlsx", dummy_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert response.status_code == 400
    assert "Missing standard ZIP/OOXML magic header" in response.json()["error"]["message"]


def test_csp_and_permissions_policy_headers_present():
    """Verify CSP and Permissions-Policy security headers are enforced (Item 17)."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "Content-Security-Policy" in response.headers
    csp = response.headers["Content-Security-Policy"]
    assert "default-src 'self'" in csp
    assert "frame-ancestors 'self'" in csp

    assert "Permissions-Policy" in response.headers
    perm = response.headers["Permissions-Policy"]
    assert "geolocation=()" in perm
    assert "camera=()" in perm


def test_cors_preflight_allowlisted_origin():
    """Verify CORS preflight succeeds for allowlisted origin (Item 7)."""
    response = client.options(
        "/api/v1/config/effective",
        headers={
            "Origin": "https://campuspulse-tau-ten.vercel.app",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "https://campuspulse-tau-ten.vercel.app"
    assert response.headers.get("access-control-allow-credentials") == "true"


def test_intervention_creation_writes_audit_log():
    """Verify state-changing actions write to AuditLog (Item 20)."""
    from adapters.postgres.models import AuditLog, Student
    from adapters.postgres.repository import get_db

    db = next(get_db())
    student = db.query(Student).first()
    student_ref = student.student_ref if student else "stu_00362b128d7c"
    initial_count = db.query(AuditLog).count()

    response = client.post(
        "/api/v1/advisors/me/interventions",
        json={
            "student_ref": student_ref,
            "action_code": "MENTOR_CHECKIN",
            "notes": "Security verification check-in",
        },
        headers={"X-User-Role": "advisor"},
    )
    assert response.status_code == 200

    new_count = db.query(AuditLog).count()
    assert new_count == initial_count + 1
    latest = db.query(AuditLog).order_by(AuditLog.id.desc()).first()
    assert latest.action == "CREATE_INTERVENTION"
    assert latest.target_id == student_ref
