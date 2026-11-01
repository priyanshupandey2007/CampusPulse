# -*- coding: utf-8 -*-
"""
Tests for pre-launch compliance and trust endpoints (§1, §2, §4, §12, §13, §32).
"""
import pytest
from fastapi.testclient import TestClient
from apps.api.main import app
from adapters.postgres.repository import get_db, Student

client = TestClient(app)


def test_public_privacy_policy_endpoint():
    """§1: Privacy policy is publicly accessible without login or cookies."""
    response = client.get("/privacy")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "CampusPulse Privacy Notice" in response.text
    assert "Legal Compliance Notice" in response.text


def test_public_terms_of_service_endpoint():
    """§2: Terms of service is publicly accessible without login or cookies."""
    response = client.get("/terms")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "CampusPulse Terms of Service" in response.text
    assert "Legal Terms of Use" in response.text


def test_terms_acceptance_recording():
    """§4: Records terms acceptance in AuditLog with user ID, version, timestamp."""
    payload = {
        "user_id": "ananya.sharma@campuspulse.edu",
        "document": "terms_and_privacy",
        "version": "1.0.0",
        "mechanism": "auth_checkbox",
    }
    response = client.post("/api/v1/auth/record-acceptance", json=payload)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "recorded"
    assert data["user_id"] == payload["user_id"]
    assert data["document"] == payload["document"]
    assert data["version"] == payload["version"]
    assert "recorded_at" in data


def test_dsar_export_student_data_authorized():
    """§13: Subject Access Request (DSAR) export returns complete structured JSON."""
    db = next(get_db())
    student = db.query(Student).first()
    assert student is not None
    ref = student.student_ref

    response = client.get(
        f"/api/v1/students/{ref}/export",
        headers={"X-User-Role": "advisor", "X-User-Email": "ananya.sharma@campuspulse.edu"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert "student_profile" in data
    assert data["student_profile"]["ref"] == ref
    assert "latest_metrics" in data
    assert "history" in data
    assert "export_metadata" in data
    assert "GDPR Art 15/20" in data["export_metadata"]["regulatory_frameworks"]


def test_dsar_export_student_data_forbidden_cross_student():
    """§13: A student cannot export another student's personal record (IDOR protection)."""
    response = client.get(
        "/api/v1/students/stu_04148c252da7/export",
        headers={
            "X-User-Role": "student",
            "X-User-Email": "student@campuspulse.edu",
            "X-User-Ref": "stu_00362b128d7c",
        },
    )
    assert response.status_code == 403


def test_privacy_rights_request_intake():
    """§13: Privacy rights request intake assigns tracking ID and SLA."""
    payload = {
        "request_type": "delete",
        "email": "student001@campuspulse.edu",
        "student_ref": "stu_00362b128d7c",
        "details": "Please purge academic traces upon cohort graduation.",
    }
    response = client.post("/api/v1/privacy/requests", json=payload)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "received"
    assert data["request_type"] == "delete"
    assert data["sla_days"] == 30
    assert data["tracking_id"].startswith("dsr_")


def test_admin_purge_expired_data():
    """§12: Admin retention purge endpoint executes retention lifecycle."""
    # Forbidden for advisor
    unauth = client.post(
        "/api/v1/admin/purge-expired-data",
        json={"retention_days": 365},
        headers={"X-User-Role": "advisor"},
    )
    assert unauth.status_code == 403

    # Authorized for admin
    auth_resp = client.post(
        "/api/v1/admin/purge-expired-data",
        json={"retention_days": 365},
        headers={"X-User-Role": "admin"},
    )
    assert auth_resp.status_code == 200
    data = auth_resp.json()["data"]
    assert data["status"] == "purged"
    assert "records_purged" in data
    assert data["retention_days"] == 365


def test_ai_assistant_disclaimer_envelope():
    """§32: AI assistant chat endpoint includes advisory disclaimer in envelope."""
    response = client.post(
        "/api/v1/assistant/chat",
        json={"query": "Who are the priority students?"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert "ai_disclaimer" in data
    assert "advisory only" in data["ai_disclaimer"].lower()
