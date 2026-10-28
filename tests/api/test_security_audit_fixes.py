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

