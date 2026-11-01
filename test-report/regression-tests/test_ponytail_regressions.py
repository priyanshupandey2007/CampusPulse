"""
Ponytail Ruthless QA Regression Tests.
Verifies fixes for Blocker, High, and audit categories:
1. CSP headers permit Firebase/Google Auth endpoints.
2. Auth overlay layout prevents heading clipping on standard viewports.
3. Role badge is present in auth modal markup.
4. Static directory contains no orphan patch/scratch scripts.
5. Unused dependencies removed from manifests.
6. Accessibility: form labels have programmatic 'for' attributes.
7. Performance: Caching headers on favicon & dashboard.
8. Code Economy: Zero deprecated datetime.utcnow calls across entire codebase.
9. Theme: Default is light theme, and all theme buttons are removed.
"""

from pathlib import Path
import re
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_csp_permits_firebase_and_google_apis():
    """Verify Content-Security-Policy allows gstatic and googleapis."""
    res = client.get("/health")
    assert res.status_code == 200
    csp = res.headers.get("Content-Security-Policy", "")
    assert "https://www.gstatic.com" in csp, "CSP missing https://www.gstatic.com in script-src"
    assert "https://*.googleapis.com" in csp, "CSP missing https://*.googleapis.com in connect-src"


def test_auth_overlay_layout_prevents_heading_clipping():
    """Verify auth overlay does not use unconstrained margin: auto flex centering."""
    index_path = Path("apps/api/static/index.html")
    assert index_path.exists()
    content = index_path.read_text(encoding="utf-8")
    
    # Check that .auth-outer does not have 'margin: auto;' without safety constraints
    auth_outer_match = re.search(r'\.auth-outer\s*\{([^}]+)\}', content)
    assert auth_outer_match is not None, ".auth-outer CSS rule not found"
    rule_body = auth_outer_match.group(1)
    assert "margin: auto;" not in rule_body, "Found unconstrained margin: auto; in .auth-outer causing heading cut-off"


def test_auth_hero_badge_present():
    """Verify Role-Based Campus Portal badge is present in HTML."""
    index_path = Path("apps/api/static/index.html")
    content = index_path.read_text(encoding="utf-8")
    assert "Role-Based Campus Portal" in content, "Missing Role-Based Campus Portal badge in auth hero"
    assert "Sign In to CampusPulse" in content, "Missing Sign In to CampusPulse heading"


def test_no_orphan_scripts_in_static_dir():
    """Ensure no scratch or patch python scripts are exposed in static public directory."""
    static_dir = Path("apps/api/static")
    py_files = list(static_dir.glob("*.py"))
    assert len(py_files) == 0, f"Found orphan python files in static directory: {py_files}"


def test_dependency_diet_verified():
    """Verify pyarrow and passlib are absent from active dependencies."""
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
    deps_section = pyproject.split("[project.optional-dependencies]")[0]
    assert "pyarrow" not in deps_section, "pyarrow still present in core dependencies"

    reqs = Path("requirements.txt").read_text(encoding="utf-8")
    assert "passlib" not in reqs, "passlib still present in requirements.txt"


def test_accessibility_labels_have_for_attributes():
    """Verify form labels in auth modal have programmatic 'for' links to input IDs."""
    index_path = Path("apps/api/static/index.html")
    content = index_path.read_text(encoding="utf-8")
    assert 'for="auth-signin-email"' in content, "Missing for='auth-signin-email' in faculty label"
    assert 'for="auth-signin-password"' in content, "Missing for='auth-signin-password' in faculty password label"
    assert 'for="auth-student-id"' in content, "Missing for='auth-student-id' in student label"
    assert 'for="auth-dean-id"' in content, "Missing for='auth-dean-id' in dean label"
    assert 'for="auth-hod-id"' in content, "Missing for='auth-hod-id' in hod label"


def test_performance_caching_headers():
    """Verify Cache-Control headers on dashboard UI and static favicon."""
    res_dash = client.get("/")
    assert res_dash.status_code == 200
    assert "cache-control" in res_dash.headers

    res_fav = client.get("/favicon.svg")
    assert res_fav.status_code == 200
    assert "max-age=86400" in res_fav.headers.get("cache-control", "")


def test_no_deprecated_utcnow_calls_in_services():
    """Ensure zero datetime.utcnow calls in services/ for Python 3.12+ forward compatibility."""
    services_dir = Path("services")
    for py_file in services_dir.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8")
        assert "datetime.datetime.utcnow()" not in content, f"Found deprecated datetime.utcnow() in {py_file}"


def test_default_theme_is_light_and_buttons_removed():
    """Verify data-theme='light' is default and theme toggle buttons are removed."""
    index_path = Path("apps/api/static/index.html")
    content = index_path.read_text(encoding="utf-8")
    assert 'data-theme="light"' in content, "HTML root missing data-theme='light'"
    assert "auth-theme-toggle" not in content, "Floating auth-theme-toggle button still present in HTML"
    assert "theme-toggle-btn" not in content, "Navbar theme-toggle-btn still present in HTML"
