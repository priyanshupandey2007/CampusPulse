# -*- coding: utf-8 -*-
"""
Adversarial Verification Suite for Milestone 4 Gate.
Owned and executed by reviewer_m4_1.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import io
import math
import pytest
from fastapi.testclient import TestClient

from apps.api.main import app, DEFAULT_THRESHOLDS, RUNTIME_THRESHOLDS
from adapters.postgres.repository import get_db, Student
from packages.domain.naac import compute_live_naac_score
from packages.domain.scores import (
    compute_academic_index,
    compute_attendance_index,
    compute_placement_index,
    compute_lms_index,
    compute_engagement_index,
    compute_skills_index,
    compute_success_score,
    determine_tier,
)

client = TestClient(app)

def run_all_adversarial_checks():
    print("=" * 80)
    print("ADVERSARIAL VERIFICATION BY REVIEWER_M4_1")
    print("=" * 80)
    
    # Reset thresholds to baseline
    client.post("/api/v1/config/thresholds/reset")
    
    # ── Check 1: R3 Threshold API Boundary Extremes & Relationships ───────────
    print("\n[Check 1] Testing Threshold API Boundaries & Relationship Invariants...")
    
    # 1.1 Standard attendance at 75% default
    res = client.get("/api/v1/config/thresholds")
    assert res.status_code == 200
    t = res.json()
    assert t["attendance_standard_min"] == 75.0, f"Expected 75.0, got {t['attendance_standard_min']}"
    assert t["attendance_emergency_min"] == 57.0, f"Expected 57.0, got {t['attendance_emergency_min']}"
    assert "0.60 * 57% + 0.40 * 100% = 74.2% < 75%" in t["emergency_floor_rationale"]
    
    # 1.2 Boundary: emergency == standard (must fail 422)
    res = client.put("/api/v1/config/thresholds", json={"attendance_emergency_min": 75.0, "attendance_standard_min": 75.0})
    assert res.status_code == 422, f"Expected 422 for equal thresholds, got {res.status_code}"
    
    # 1.3 Boundary: emergency > standard (must fail 422)
    res = client.put("/api/v1/config/thresholds", json={"attendance_emergency_min": 76.0, "attendance_standard_min": 75.0})
    assert res.status_code == 422, f"Expected 422, got {res.status_code}"
    
    # 1.4 Single field update violating existing counterpart:
    # standard currently 75.0. Try setting emergency to 80.0
    res = client.put("/api/v1/config/thresholds", json={"attendance_emergency_min": 80.0})
    assert res.status_code == 422, f"Expected 422, got {res.status_code}"
    
    # 1.5 CGPA boundary: emergency == warning (must fail 422)
    res = client.put("/api/v1/config/thresholds", json={"cgpa_emergency_min": 6.0, "cgpa_warning_min": 6.0})
    assert res.status_code == 422, f"Expected 422, got {res.status_code}"
    
    # 1.6 CGPA boundary: emergency > warning (must fail 422)
    res = client.put("/api/v1/config/thresholds", json={"cgpa_emergency_min": 7.0, "cgpa_warning_min": 6.0})
    assert res.status_code == 422, f"Expected 422, got {res.status_code}"
    
    # 1.7 Out-of-bounds inputs (<0, >100, >10)
    for bad_payload in [
        {"attendance_standard_min": -0.1},
        {"attendance_standard_min": 100.1},
        {"cgpa_warning_min": -0.1},
        {"cgpa_warning_min": 10.1},
        {"backlog_warning_max": -1},
        {"backlog_warning_max": 25},
    ]:
        res = client.put("/api/v1/config/thresholds", json=bad_payload)
        assert res.status_code == 422, f"Expected 422 for {bad_payload}, got {res.status_code}"

    # 1.8 Reset works reliably
    res = client.post("/api/v1/config/thresholds/reset")
    assert res.status_code == 200
    assert res.json()["thresholds"]["attendance_standard_min"] == 75.0
    print("  -> Check 1 PASSED: All boundary extremes and relationship invariants strictly enforced.")

    # ── Check 2: Dynamic Propagation to Action List & Effective Config ────────
    print("\n[Check 2] Testing Dynamic Propagation of Thresholds...")
    
    # Test effective config reflects runtime threshold overlay
    res = client.put("/api/v1/config/thresholds", json={"attendance_standard_min": 82.0, "attendance_emergency_min": 62.0})
    assert res.status_code == 200
    eff = client.get("/api/v1/config/effective").json()["data"]
    assert eff["floors"]["attendance_standard_min"] == 82.0
    assert eff["floors"]["attendance_min"] == 62.0
    assert eff["thresholds"]["attendance_standard_min"] == 82.0
    
    # Test advisor action list reflects changes
    headers = {"X-User-Role": "advisor", "X-User-Email": "advisor@campuspulse.edu"}
    act_res = client.get("/api/v1/advisors/me/action-list?limit=10", headers=headers)
    assert act_res.status_code == 200
    act_data = act_res.json()["data"]
    assert act_data["thresholds"]["attendance_standard_min"] == 82.0
    assert act_data["thresholds"]["attendance_emergency_min"] == 62.0
    
    # Reset back to default
    client.post("/api/v1/config/thresholds/reset")
    eff2 = client.get("/api/v1/config/effective").json()["data"]
    assert eff2["floors"]["attendance_standard_min"] == 75.0
    assert eff2["floors"]["attendance_min"] == 57.0
    print("  -> Check 2 PASSED: Dynamic propagation to effective config and action list verified.")

    # ── Check 3: R2 Scoring Determinism & ML Decoupling ───────────────────────
    print("\n[Check 3] Testing 100% Deterministic Pure AST Scoring & ML Decoupling...")
    
    # Verify domain calculation returns identical results for 100 iterations
    for _ in range(100):
        s_score = compute_success_score(
            academic=compute_academic_index(8.5, 0),
            attendance=compute_attendance_index(82.0, 0),
            placement=compute_placement_index(75.0, 80.0, 70.0),
            lms=compute_lms_index(85.0, 90.0),
            engagement=compute_engagement_index(2, 1, 1, 1),
            skills=compute_skills_index(80.0, 75.0),
            weights={"academic": 0.25, "attendance": 0.20, "placement": 0.20, "lms": 0.15, "engagement": 0.10, "skills": 0.10}
        )
        assert abs(s_score - 76.225) < 1e-9, f"Non-deterministic score calculation: {s_score}"
        
    # Verify ML agreement check does NOT alter rules tier
    ml_res = client.post("/api/v1/ml/agreement-check", json={
        "features": {"academic": 80.0, "attendance": 80.0, "placement": 70.0, "lms": 75.0},
        "rules_tier": "watchlist",
        "enabled": True
    })
    assert ml_res.status_code == 200
    ml_data = ml_res.json()["data"]
    assert ml_data["rules_tier"] == "watchlist"
    assert ml_data["scoring_engine"] == "100% deterministic AST"
    assert ml_data["ml_role"] == "audited_fairness_proxy_secondary"
    print("  -> Check 3 PASSED: Scoring is 100% deterministic pure AST; ML is an audited proxy only.")

    # ── Check 4: R4 Ingestion Security, Limits & NAAC Contract ────────────────
    print("\n[Check 4] Testing Ingestion Extensions, Limits & NAAC Contract...")
    
    # 4.1 Ingestion extensions rejected
    for ext, content in [(".exe", b"MZ"), (".sh", b"#!/bin/sh"), (".pdf", b"%PDF")]:
        f = io.BytesIO(content)
        r = client.post(
            "/api/v1/ingest/upload",
            files={"file": (f"test{ext}", f, "application/octet-stream")},
            headers={"X-User-Role": "admin", "X-User-Email": "admin@campuspulse.edu"}
        )
        assert r.status_code == 400
        assert "Invalid file extension" in r.json()["error"]["message"]
        
    # 4.2 Ingestion 15MB limit
    f_large = io.BytesIO(b"X" * (15 * 1024 * 1024 + 1024))
    r_large = client.post(
        "/api/v1/ingest/upload",
        files={"file": ("big.csv", f_large, "text/csv")},
        headers={"X-User-Role": "admin", "X-User-Email": "admin@campuspulse.edu"}
    )
    assert r_large.status_code == 413
    assert "File exceeds maximum allowed size of 15MB" in r_large.json()["error"]["message"]
    
    # 4.3 Student role forbidden
    f_ok = io.BytesIO(b"Roll Number,Name\n2023CSE001,Test\n")
    r_stud = client.post(
        "/api/v1/ingest/upload",
        files={"file": ("test.csv", f_ok, "text/csv")},
        headers={"X-User-Role": "student", "X-User-Email": "student@campuspulse.edu"}
    )
    assert r_stud.status_code == 403
    
    # 4.4 NAAC zero-regression contract
    naac_res = compute_live_naac_score()
    assert naac_res["grade"] == "A++", f"Expected grade A++, got {naac_res['grade']}"
    assert naac_res["cgpa"] >= 3.51
    print("  -> Check 4 PASSED: Ingestion security gates and NAAC A++ zero regression contract verified.")

    # ── Check 5: R1 Frontend Navigation Hierarchy & Routes ────────────────────
    print("\n[Check 5] Testing Frontend Navigation Hierarchy, Intact IDs & Routes...")
    
    index_res = client.get("/")
    assert index_res.status_code == 200
    html = index_res.text
    
    # Primary Advisor navigation checks
    assert "Early-Warning &amp; Triage" in html
    assert "action-list" in html
    assert "student-reports" in html
    assert "interventions-os" in html
    assert "ingestion-pipeline" in html
    
    # Secondary student practice labs
    assert "Student Practice Labs (Secondary)" in html
    for lab_route in ["learn-modules", "lab-practice", "ai-mentor", "ai-interviewer", "code-editor", "project-bank"]:
        assert f"switchNav('{lab_route}')" in html, f"Missing route switchNav('{lab_route}')"
        assert f'id="view-{lab_route}"' in html, f"Missing view-container id=\"view-{lab_route}\""
        
    # Modal and badges
    assert 'id="modal-thresholds"' in html
    assert 'id="nav-count"' in html
    assert 'id="nav-interventions-count"' in html
    assert "NAAC SSR Readiness &amp; Evidence Dossier" in html or "NAAC SSR Readiness & Evidence Dossier" in html
    assert "Statutory Metric Validation Notice" in html
    assert "Week 9 point of mathematical impossibility" in html
    print("  -> Check 5 PASSED: Frontend navigation hierarchy, DOM IDs, and routes intact.")

    print("\n" + "=" * 80)
    print("ALL ADVERSARIAL CHECKS PASSED WITH ZERO ERRORS!")
    print("=" * 80)

if __name__ == "__main__":
    run_all_adversarial_checks()
