"""
Tests for Production-Grade Pages, System States, and Lifecycle Endpoints.
Verifies compliance with the Production Page & UX State Audit.
"""

from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_security_txt_endpoint():
    """Verify RFC 9116 security.txt is accessible and well-formatted."""
    response = client.get("/.well-known/security.txt")
    assert response.status_code == 200
    assert "text/plain" in response.headers.get("content-type", "")
    assert "Contact: mailto:security@campuspulse.edu" in response.text
    assert "Expires:" in response.text
    assert "Canonical:" in response.text


def test_system_maintenance_status():
    """Verify maintenance status endpoint returns operational status envelope."""
    response = client.get("/api/v1/system/maintenance-status")
    assert response.status_code == 200
    data = response.json().get("data", {})
    assert "maintenance_active" in data
    assert data["status"] in ("operational", "maintenance")
    assert "version" in data


def test_forgot_password_anti_enumeration():
    """Verify forgot-password endpoint logs request and returns generic confirmation without account enumeration."""
    # Test with student email
    resp1 = client.post("/api/v1/auth/forgot-password", json={"email": "priyanshu@campuspulse.edu"})
    assert resp1.status_code == 200
    body1 = resp1.json()
    assert body1["data"]["status"] == "dispatched"
    assert "If an account exists" in body1["data"]["message"]

    # Test with non-existent email
    resp2 = client.post("/api/v1/auth/forgot-password", json={"email": "nonexistent.user.999@univ.edu"})
    assert resp2.status_code == 200
    body2 = resp2.json()
    assert body2["data"]["status"] == "dispatched"
    # Responses must be identical to prevent enumeration
    assert body1["data"]["message"] == body2["data"]["message"]


def test_legal_and_compliance_public_endpoints():
    """Verify all applicable legal and compliance documents are publicly readable without auth."""
    endpoints = [
        ("/cookies", "Cookie"),
        ("/accessibility", "Accessibility"),
        ("/security", "Security"),
        ("/acceptable-use", "Acceptable Use"),
        ("/dpa", "Data Processing Agreement"),
        ("/responsible-disclosure", "Responsible Disclosure"),
        ("/privacy", "Privacy"),
        ("/terms", "Terms"),
    ]
    for path, expected_text in endpoints:
        resp = client.get(path)
        assert resp.status_code == 200, f"Failed for {path}"
        assert "text/html" in resp.headers.get("content-type", "")
        assert expected_text in resp.text, f"Missing {expected_text} in {path}"


def test_web_404_html_navigation():
    """Verify non-API HTML requests return the accessible HTML 404 page."""
    resp = client.get("/non-existent-web-page-1234", headers={"Accept": "text/html"})
    assert resp.status_code == 404
    assert "text/html" in resp.headers.get("content-type", "")
    assert "Page or Route Not Found" in resp.text
    assert "Return to CampusPulse Dashboard" in resp.text


def test_frontend_production_views_and_modals_exist():
    """Verify all applicable production views, modals, and UX state elements exist in the root index.html."""
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.text

    # Views
    required_views = [
        'id="view-help-center"',
        'id="view-accessibility"',
        'id="view-cookie-policy"',
        'id="view-security-policy"',
        'id="view-responsible-disclosure"',
        'id="view-acceptable-use"',
        'id="view-dpa"',
        'id="view-terms-conditions"',
        'id="view-privacy-policy"',
        'id="view-404"',
        'id="view-403"',
        'id="view-500"',
        'id="view-maintenance"',
    ]
    for view in required_views:
        assert view in html, f"Missing view element: {view}"

    # Modals
    required_modals = [
        'id="modal-forgot-password"',
        'id="modal-account-settings"',
        'id="modal-onboarding"',
        'id="modal-session-expired"',
    ]
    for modal in required_modals:
        assert modal in html, f"Missing modal element: {modal}"

    # System states
    assert 'id="offline-banner"' in html, "Missing offline banner"
    assert "UNIVERSAL_VIEWS" in html, "Missing UNIVERSAL_VIEWS router mapping"
    assert "clearStudentSearchAndFilters" in html, "Missing search reset function"
    assert "exportMyUserData" in html, "Missing DSAR export function"
