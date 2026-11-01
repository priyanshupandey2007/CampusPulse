# Ruthless QA Fix Plan

**Project**: CampusPulse  
**Branch**: `hardcore-test/2026-11-01`  
**Audit Standard**: Ponytail Full Audit  

---

## 1. Quick Wins (< 1 Hour) — Already Applied in Branch

### Fix 1: Auth Screen Viewport Clipping & Heading Visibility (PONY-01)
- **Path**: `apps/api/static/index.html`
- **Root Cause**: `.auth-outer` inside `#auth-overlay-screen` used `margin: auto;` in flex column with `overflow-y: auto`. On screens with height < ~850px, negative free space centered the top of the card above `y = 0`, permanently clipping the `<h1>Sign In to CampusPulse</h1>` and hero badge.
- **Diff / Code Applied**:
  ```css
  #auth-overlay-screen {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: #08090d;
    z-index: 500;
    display: none;
    overflow-y: auto;
    padding: 24px 16px 48px;
    box-sizing: border-box;
  }
  .auth-outer {
    width: 460px;
    max-width: 100%;
    margin: 16px auto 32px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
  }
  ```
- **Re-test Step**: Run `pytest test-report/regression-tests/test_ponytail_regressions.py::test_auth_overlay_layout_prevents_heading_clipping` and visually inspect `http://localhost:8000/` at 1366x768 viewport.

### Fix 2: Content-Security-Policy Blocking Firebase & Google OAuth (PONY-02)
- **Path**: `apps/api/main.py`
- **Root Cause**: CSP `script-src` only permitted `cdn.jsdelivr.net`, and `connect-src` only permitted `'self'`. Strict browsers threw CSP violations on Firebase SDKs from `gstatic.com` and token endpoints at `googleapis.com`.
- **Diff / Code Applied**:
  ```python
  response.headers["Content-Security-Policy"] = (
      "default-src 'self'; "
      "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://www.gstatic.com; "
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
      "font-src 'self' https://fonts.gstatic.com; "
      "img-src 'self' data: https:; "
      "connect-src 'self' https://*.googleapis.com https://identitytoolkit.googleapis.com https://securetoken.googleapis.com; "
      "frame-src 'self' https://*.firebaseapp.com; "
      "frame-ancestors 'self'; "
      "base-uri 'self'; "
      "form-action 'self';"
  )
  ```
- **Re-test Step**: Run `pytest test-report/regression-tests/test_ponytail_regressions.py::test_csp_permits_firebase_and_google_apis`.

### Fix 3: Delete Publicly Exposed Scratch Script (PONY-03)
- **Path**: `apps/api/static/patch.py`
- **Root Cause**: Leftover developer scratch script in public static assets directory.
- **Action**: Deleted `apps/api/static/patch.py` (saved 16.5 KB, eliminated information disclosure).
- **Re-test Step**: Run `pytest test-report/regression-tests/test_ponytail_regressions.py::test_no_orphan_scripts_in_static_dir`.

### Fix 4: Eliminate 217 Lines of Dead Code in main.py (PONY-04)
- **Path**: `apps/api/main.py`
- **Root Cause**: Dangling un-invoked return payload inside `get_competitive_dashboard_widget()`.
- **Action**: Removed lines 2202–2419.
- **Re-test Step**: Run `pytest tests/api/test_competitive_intelligence.py`.

---

## 2. This Week (< 1 Day)

### Project 1: SVG Sprite System for Client HTML
- **Problem**: 265 hardcoded SVG strings across 11,000 lines of `index.html` bloating HTML payload to 700 KB.
- **Fix**: Create an SVG symbol sprite `<svg style="display:none"><symbol id="icon-..."><path ...></symbol></svg>` at the top of the body and replace duplicated SVG markup with `<svg class="icon"><use href="#icon-..."/></svg>`.
- **Expected Saving**: ~65 KB compressed transfer size, reduced DOM node count.

### Project 2: Prune Unused Heavy Dependencies from Lockfiles
- **Problem**: `asyncpg` (12 MB) and `alembic` (4 MB) installed in production images but not actively used (SQLite / synchronous SQLAlchemy engine used directly).
- **Fix**: Remove `asyncpg` and `alembic` from `pyproject.toml` dependencies until asynchronous connection pooling or Alembic schema migrations are explicitly enabled.

---

## 3. Bigger Projects (> 1 Day)

### Project 1: Modularize index.html into Component Bundles
- **Problem**: Single 11,082-line HTML file mixes styles, templates, logic, and dataset defaults.
- **Fix**: Split into `src/styles/`, `src/components/`, `src/modules/` with a lightweight, no-build asset aggregator or clean ESM module imports (`type="module"` native in all modern browsers).
- **Ponytail Ladder Justification**: Native ES Modules require zero bundler or build step (`<script type="module" src="/static/js/app.js">`), keeping build steps at zero.

