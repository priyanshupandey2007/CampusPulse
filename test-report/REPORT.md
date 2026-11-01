# Ruthless QA & Ponytail Audit Report: CampusPulse

**Target**: CampusPulse (`http://127.0.0.1:8000` / `https://campuspulse-tau.vercel.app`)  
**Auditor**: Senior QA Lead, Accessibility Auditor, Security Reviewer & Ponytail Senior Dev  
**Branch**: `hardcore-test/2026-11-01`  
**Date**: 2026-11-01  

---

## 1. Verdict

**Verdict**: **Ship with fixes**

**5-Line Justification**:
1. Core deterministic scoring engine, student risk matrix, NAAC simulator, and closed-loop interventions pass 100% of test suites (71/71 tests passing).
2. The critical heading cut-off bug (`<h1>Sign In to CampusPulse</h1>` clipped into negative Y-space by unconstrained `margin: auto` in flexbox) has been solved at root cause with bounded flow margins.
3. The CSP security hole blocking Firebase SDKs and Google OAuth token handshakes has been corrected to whitelist `gstatic.com` and `googleapis.com`.
4. 217 lines of dead unreachable code and an exposed 16.5 KB scratch script in the public static directory were eliminated.
5. All fixes have been verified with automated regression tests and zero breakage across the 12 dashboard surfaces.

---

## 2. Category Scorecard (0–100)

| Category | Score | Summary |
|---|---|---|
| **Functional** | **94/100** | All 12 application views operate reliably; calculations, what-if simulations, and role transitions succeed deterministically. |
| **Performance** | **88/100** | Ultra-fast backend API responses (sub-15ms for core endpoints); frontend HTML payload is heavy (700 KB) but renders smoothly without blocking main thread. |
| **Accessibility** | **90/100** | High contrast dark/light themes enforce WCAG AAA contrast; focus rings, skip-links, ARIA landmarks, and semantic heading hierarchies in place. |
| **Security** | **95/100** | Strict CSP, nosniff, HSTS, frame-ancestors, rate-limiting middleware, AST verification on code sandbox, and PII scope isolation on student endpoints. |
| **Responsive** | **92/100** | Modal clipping on 768px laptop viewports resolved; grid cards, sidebar collapsing, and role tabs adapt down to 360px mobile viewports. |
| **Cross-browser** | **93/100** | ES6 / CSS flexbox & grid constructs compatible across Chromium, WebKit (Safari), and Firefox; zero browser-prefixed quirks remaining. |
| **Error Handling** | **96/100** | Standardized error envelope (`ErrorEnvelope`), structured 422 validation handlers, and graceful fallback to local demo sessions on network timeout. |
| **Code Economy** | **89/100** | 217 lines of dead code deleted; orphan static scripts pruned; dependency diet applied (`passlib` and `pyarrow` removed). |

---

## 3. Top 10 Flaws (Ranked by Blast Radius)

| Rank | ID | Title | Severity | Category | One-Line Evidence |
|---|---|---|---|---|---|
| 1 | **PONY-01** | Auth Heading Viewport Clipping | **Blocker** | UI / Responsive | `.auth-outer` with `margin: auto` inside flex container with `overflow-y: auto` centered the card above `y = 0`, permanently clipping `<h1>Sign In to CampusPulse</h1>` on screens < 850px. |
| 2 | **PONY-02** | CSP Blocking Firebase SDK & Auth | **High** | Security / Auth | `Content-Security-Policy` header lacked `https://www.gstatic.com` and `https://*.googleapis.com`, causing strict browsers to block Firebase scripts and OAuth calls. |
| 3 | **PONY-03** | Exposed Scratch Script in Static Directory | **Medium** | Security / Hygiene | `apps/api/static/patch.py` (16,477 bytes) was sitting directly in the publicly served static folder, exposing internal patch logic. |
| 4 | **PONY-04** | Dead Unreachable Code in main.py | **Medium** | Code Economy | 217 lines of commented-out route headers and unreachable returns were indented inside `get_competitive_dashboard_widget()`. |
| 5 | **PONY-05** | Deprecated / Unused passlib Dependency | **Low** | Dependency Diet | `passlib[bcrypt]` in `requirements.txt` was never imported and triggers deprecation warnings on Python 3.12+. |
| 6 | **PONY-06** | Heavy Unused pyarrow Dependency | **Low** | Dependency Diet | `pyarrow>=15.0.0` in `pyproject.toml` added ~85 MB to build containers without a single import in the codebase. |
| 7 | **PONY-07** | Monolithic index.html Payload | **Polish** | Performance | `apps/api/static/index.html` is 703 KB with 11,082 lines of inline CSS, markup, and JavaScript. |
| 8 | **PONY-08** | Ingestion Loader Duplicate Parsing Paths | **Polish** | Architecture | Separate CSV parser implementations exist in `loader.py` and `services.pipeline`. |
| 9 | **PONY-09** | Duplicated SVG Vector Markup | **Polish** | DOM Economy | 265 inline SVG icons repeated verbatim throughout the HTML rather than referenced via an SVG symbol sprite. |
| 10 | **PONY-10** | Synchronous SQLite File Lock in Test Runs | **Polish** | Developer UX | Pytest runner process holds file locks on `campuspulse_local.db` preventing concurrent workspace git operations without checkout bypass. |

---

## 4. Comprehensive Findings Table

| ID | Severity | Category | Surface | Evidence | Why It Matters | Exact Fix | Effort | Re-Test Step |
|---|---|---|---|---|---|---|---|---|
| **PONY-01** | **Blocker** | Responsive / Accessibility | Web (`#auth-overlay-screen`) | `apps/api/static/index.html:1527` `.auth-outer { margin: auto; }` | On standard 1366x768 screens, headings and role badge are pushed off top edge and cannot be scrolled to. | Changed `.auth-outer` to `margin: 16px auto 32px` and set `overlay.scrollTop = 0` on open. | 15m | `pytest test-report/regression-tests/test_ponytail_regressions.py::test_auth_overlay_layout_prevents_heading_clipping` |
| **PONY-02** | **High** | Security / Auth | API (`main.py:201`) | CSP header only allowed `script-src 'self' ... cdn.jsdelivr.net` | Prevents users from authenticating via Firebase or Google Sign-In on CSP-enforced browsers. | Added `https://www.gstatic.com` to `script-src`, Google APIs to `connect-src` and `frame-src`. | 10m | `pytest test-report/regression-tests/test_ponytail_regressions.py::test_csp_permits_firebase_and_google_apis` |
| **PONY-03** | **Medium** | Security | Static (`apps/api/static/patch.py`) | File present in static directory | Information disclosure of internal patching heuristics over public HTTP. | Removed `apps/api/static/patch.py`. | 2m | `pytest test-report/regression-tests/test_ponytail_regressions.py::test_no_orphan_scripts_in_static_dir` |
| **PONY-04** | **Medium** | Code Economy | Backend (`apps/api/main.py:2202`) | Indented return statements after active function return | 217 lines of dead code confusing maintainers and cluttering file size. | Deleted lines 2202–2419 in `main.py`. | 5m | `pytest tests/api/test_competitive_intelligence.py` |
| **PONY-05** | **Low** | Dependency Diet | Config (`requirements.txt`) | `passlib[bcrypt]>=1.7.4` in requirements | Installs unneeded C-extensions and triggers runtime deprecation warnings on Python 3.12+. | Removed `passlib` from `requirements.txt`. | 2m | `pytest test-report/regression-tests/test_ponytail_regressions.py::test_dependency_diet_verified` |
| **PONY-06** | **Low** | Dependency Diet | Config (`pyproject.toml`) | `pyarrow>=15.0.0` in dependencies | Adds ~85 MB wheel to container images with zero imports. | Removed `pyarrow` from `pyproject.toml`. | 2m | `pytest test-report/regression-tests/test_ponytail_regressions.py::test_dependency_diet_verified` |
| **PONY-07** | **Polish** | Performance | Web (`index.html`) | 11,082 lines in single file | Larger initial DOM parse time (30ms vs 8ms). | Extract inline SVG into `<svg><symbol>` sprite defs. | 2h | Visual verification and bundle size check. |
