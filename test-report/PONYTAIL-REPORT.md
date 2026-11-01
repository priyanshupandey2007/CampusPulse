# Ponytail Senior Dev Audit Report

**Auditor Role**: Ruthless Senior QA & Ponytail Lead  
**Audit Target**: CampusPulse (Local: `http://127.0.0.1:8000`, Staging: `https://campuspulse-tau.vercel.app`)  
**Level**: Full  
**Branch**: `hardcore-test/2026-11-01`  

---

## 1. Delete List (Dead Code & Junk)

| File Path | Lines / Region | Saved | Why Safe to Delete |
|---|---|---|---|
| `apps/api/main.py` | Lines 2202–2419 | 217 lines | Dangling dead code: commented-out KPMG route headers followed by indented, unreachable returns inside `get_competitive_dashboard_widget()`. Never executed by any caller. |
| `apps/api/static/patch.py` | Entire file | 16,477 bytes | Abandoned one-off patching scratch script sitting in the public static assets directory. Information disclosure and zero runtime usage. |
| `apps/api/static/index.html` | Redundant inline button override classes | ~120 lines | Multiple duplicate inline CSS rules for `.auth-terms-box` and conflicting color declarations that overrode base design system tokens. |

---

## 2. Replace List (Custom Code → Native / Stdlib)

| File / Location | What Was Written | What Replaces It | Why |
|---|---|---|---|
| `apps/api/static/index.html` (`.auth-outer`) | Flexbox vertical auto-centering (`margin: auto;` in flex column) | Native flow spacing: `margin: 16px auto 32px;` with top padding | Native block margins prevent negative-Y coordinate overflow when content height exceeds standard 768px laptop viewports. Eliminates clipped headings. |
| `apps/api/main.py` | Hand-rolled inline rate limiting memory store cleanup | `lru_cache` or bounded dict retention | Standard dictionary eviction prevents potential unbounded memory growth under sustained distributed IP scanning. |
| `apps/api/static/index.html` | 265 hardcoded SVG icons duplicated inline across views | Reusable `<svg class="icon"><use href="#icon-id"/></svg>` sprite defs | Cuts ~65 KB of DOM weight from HTML parse tree without external network requests. |

---

## 3. Reuse List (Wheels Reinvented)

| Wheel Found | Exists Elsewhere In Codebase | Fix / Unified Target |
|---|---|---|
| Ingestion parsing logic | Duplicate CSV parsing routines in `services/ingestion/loader.py` and `apps/api/main.py` | Route all uploads through `services.pipeline.execute_pipeline` (single ingress point). |
| Error formatting | Ad-hoc error dicts in older mock endpoints vs `make_envelope` | Enforce `make_envelope(..., error=...)` or FastAPI HTTPException handlers across all routes. |
| Dark/Light Theme Switching | Ad-hoc theme toggle handlers in auth modal vs navbar | Unified `window.toggleTheme()` hook bound to `document.documentElement[data-theme]`. |

---

## 4. Dependency Diet

| Package | Status | Weight | Reason / Action |
|---|---|---|---|
| `passlib[bcrypt]` | Dropped from `requirements.txt` | ~2.5 MB | Never imported. Deprecated in Python 3.12+ (raises bcrypt/hashlib issues). Auth uses Firebase client tokens & SHA-256 signatures. |
| `pyarrow` | Dropped from `pyproject.toml` | ~85 MB | Not imported once in the entire repository (`pandas` uses native engine for current CSV/Excel workloads). |
| `asyncpg` | Flagged for pruning | ~12 MB | Database layer runs synchronous SQLAlchemy engine (`create_engine(DATABASE_URL.replace("+asyncpg", ""))`). |
| `alembic` | Flagged for pruning | ~4 MB | No Alembic migrations directory exists; database initialized directly via `Base.metadata.create_all(bind=engine)`. |

---

## 5. Must-Fix Risks (Never Lazy About)

| Finding ID | Severity | Area | Evidence | Root-Cause Fix |
|---|---|---|---|---|
| **PONY-01** | **Blocker** | UI / Viewport Clipping | On standard 1366x768 screens, `#auth-overlay-screen` centered `.auth-outer` into negative Y space, clipping `<h1>Sign In to CampusPulse</h1>` and hero badge off screen. | Changed `.auth-outer` margin from `auto` to `16px auto 32px` and set `overlay.scrollTop = 0` on modal display. |
| **PONY-02** | **High** | Security / CSP Blocking Auth | `Content-Security-Policy` header in `main.py` omitted `https://www.gstatic.com` from `script-src` and `https://*.googleapis.com` from `connect-src`. Strict browsers blocked Firebase scripts. | Added `https://www.gstatic.com` to `script-src` and Google Identity endpoints to `connect-src` and `frame-src`. |
| **PONY-03** | **Medium** | Information Disclosure | `apps/api/static/patch.py` exposed internal codebase patch logic publicly over HTTP. | Deleted `patch.py` from `apps/api/static/`. |
| **PONY-04** | **Medium** | Dead Code Accumulation | 217 lines of dangling code inside `get_competitive_dashboard_widget()` in `main.py`. | Deleted dead lines 2202–2419. |

---

## 6. Ponytail Verdict

**The single first thing to fix before anything else**:
Ensure the authentication screen never uses unconstrained `margin: auto` inside a flex container with `overflow-y: auto`. Flex vertical centering without bounds causes negative coordinates that cannot be reached by scrolling, permanently hiding headings and critical CTAs on standard laptop screens.

