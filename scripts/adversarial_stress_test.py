# -*- coding: utf-8 -*-
"""
Adversarial Stress Test Harness for Milestone 4 Gate.
Tests:
1. Threshold API Boundary Extremes:
   - attendance = 0.0, 100.0, 100.1, -1.0
   - float precision (e.g. 75.123456789, epsilon diffs 75.0000001 vs 75.0)
   - emergency == standard
   - emergency > standard
   - cgpa boundary extremes & relationships
   - backlog boundary extremes & relationships
2. Concurrency & Repeated Resets:
   - Adversarial Rate Limit verification (HTTP 429 under DDoS / brute force)
   - High-throughput multi-threaded concurrent updates, gets, and resets (500 ops across 16 threads)
   - Post-concurrency canonical state invariant verification
3. Deterministic Scoring Reproducibility:
   - 100 rapid repeated executions of domain scoring on 50 synthetic student edge cases
   - 100 rapid repeated executions of API action-list endpoint
   - 100 rapid repeated executions of student explain AST calculation
   - Cryptographic SHA-256 hashing across iterations to verify 0.000% variance
"""

import concurrent.futures
import hashlib
import json
import random
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient

import apps.api.main as api_main
from apps.api.main import app, DEFAULT_THRESHOLDS, RUNTIME_THRESHOLDS, RATE_LIMIT_STORE
from packages.domain.scores import (
    compute_academic_index,
    compute_attendance_index,
    compute_placement_index,
    compute_lms_index,
    compute_engagement_index,
    compute_skills_index,
    compute_success_score,
    classify_momentum,
    determine_tier,
    compute_priority_score,
    Tier,
    Momentum,
)

client = TestClient(app)


def test_boundary_extremes():
    print("\n" + "=" * 80)
    print("TEST SUITE 1: THRESHOLD API BOUNDARY EXTREMES")
    print("=" * 80)

    # Clear rate limits and reset thresholds before starting
    RATE_LIMIT_STORE.clear()
    res = client.post("/api/v1/config/thresholds/reset")
    assert res.status_code == 200

    results = []

    # 1. attendance = 0.0: Valid when standard is positive and greater than 0.0
    # Case 1A: emergency = 0.0, standard = 75.0 -> Valid
    r = client.put("/api/v1/config/thresholds", json={"attendance_emergency_min": 0.0, "attendance_standard_min": 75.0})
    passed = (r.status_code == 200 and r.json()["thresholds"]["attendance_emergency_min"] == 0.0)
    results.append(("attendance_emergency_min = 0.0 (valid lower bound)", passed, r.status_code))
    print(f"[{'PASS' if passed else 'FAIL'}] attendance_emergency_min = 0.0: status {r.status_code}")

    # Case 1B: standard = 0.0 with emergency = 0.0 -> emergency == standard -> 422
    r = client.put("/api/v1/config/thresholds", json={"attendance_emergency_min": 0.0, "attendance_standard_min": 0.0})
    passed = (r.status_code == 422 and r.json()["error"]["code"] == "VALIDATION_ERROR")
    results.append(("attendance = 0.0 for both (emergency == standard)", passed, r.status_code))
    print(f"[{'PASS' if passed else 'FAIL'}] attendance standard = 0.0 & emerg = 0.0: status {r.status_code}")

    # Case 1C: standard = 0.0 with default emergency (57.0) -> emerg > std -> 422
    client.post("/api/v1/config/thresholds/reset")
    r = client.put("/api/v1/config/thresholds", json={"attendance_standard_min": 0.0})
    passed = (r.status_code == 422 and r.json()["error"]["code"] == "VALIDATION_ERROR")
    results.append(("attendance_standard_min = 0.0 (violates emerg < std)", passed, r.status_code))
    print(f"[{'PASS' if passed else 'FAIL'}] attendance_standard_min = 0.0: status {r.status_code}")

    # 2. attendance = 100.0:
    # Case 2A: standard = 100.0 with emergency = 57.0 -> Valid
    r = client.put("/api/v1/config/thresholds", json={"attendance_standard_min": 100.0})
    passed = (r.status_code == 200 and r.json()["thresholds"]["attendance_standard_min"] == 100.0)
    results.append(("attendance_standard_min = 100.0 (valid upper bound)", passed, r.status_code))
    print(f"[{'PASS' if passed else 'FAIL'}] attendance_standard_min = 100.0: status {r.status_code}")

    # Case 2B: emergency = 100.0 with standard = 100.0 -> emerg == std -> 422
    r = client.put("/api/v1/config/thresholds", json={"attendance_emergency_min": 100.0, "attendance_standard_min": 100.0})
    passed = (r.status_code == 422 and r.json()["error"]["code"] == "VALIDATION_ERROR")
    results.append(("attendance_emergency_min = 100.0 (emerg == std)", passed, r.status_code))
    print(f"[{'PASS' if passed else 'FAIL'}] attendance_emergency_min = 100.0 & std = 100.0: status {r.status_code}")

    # 3. attendance = 100.1 (Out of bounds > 100.0) -> 422
    client.post("/api/v1/config/thresholds/reset")
    r1 = client.put("/api/v1/config/thresholds", json={"attendance_standard_min": 100.1})
    r2 = client.put("/api/v1/config/thresholds", json={"attendance_emergency_min": 100.1})
    passed = (r1.status_code == 422 and r2.status_code == 422)
    results.append(("attendance = 100.1 (upper boundary exceeded)", passed, (r1.status_code, r2.status_code)))
    print(f"[{'PASS' if passed else 'FAIL'}] attendance = 100.1: status {r1.status_code}, {r2.status_code}")

    # 4. attendance = -1.0 (Out of bounds < 0.0) -> 422
    r1 = client.put("/api/v1/config/thresholds", json={"attendance_standard_min": -1.0})
    r2 = client.put("/api/v1/config/thresholds", json={"attendance_emergency_min": -1.0})
    passed = (r1.status_code == 422 and r2.status_code == 422)
    results.append(("attendance = -1.0 (negative boundary breach)", passed, (r1.status_code, r2.status_code)))
    print(f"[{'PASS' if passed else 'FAIL'}] attendance = -1.0: status {r1.status_code}, {r2.status_code}")

    # 5. float precision:
    # 5A: High precision fractional floats
    r = client.put("/api/v1/config/thresholds", json={
        "attendance_standard_min": 75.123456789,
        "attendance_emergency_min": 57.987654321,
    })
    passed = (r.status_code == 200 and abs(r.json()["thresholds"]["attendance_standard_min"] - 75.123456789) < 1e-6)
    results.append(("float precision (high precision fractional floats)", passed, r.status_code))
    print(f"[{'PASS' if passed else 'FAIL'}] High precision floats (75.123456789, 57.987654321): status {r.status_code}")

    # 5B: Infinitesimal epsilon difference (standard = 75.00001, emergency = 75.00000)
    r = client.put("/api/v1/config/thresholds", json={
        "attendance_standard_min": 75.00001,
        "attendance_emergency_min": 75.00000,
    })
    passed = (r.status_code == 200 and r.json()["thresholds"]["attendance_standard_min"] > r.json()["thresholds"]["attendance_emergency_min"])
    results.append(("float precision (epsilon separation 1e-5)", passed, r.status_code))
    print(f"[{'PASS' if passed else 'FAIL'}] Epsilon separation (75.00001 vs 75.00000): status {r.status_code}")

    # 6. emergency == standard (attendance & CGPA)
    client.post("/api/v1/config/thresholds/reset")
    r_att = client.put("/api/v1/config/thresholds", json={"attendance_emergency_min": 75.0, "attendance_standard_min": 75.0})
    r_cgpa = client.put("/api/v1/config/thresholds", json={"cgpa_emergency_min": 6.0, "cgpa_warning_min": 6.0})
    passed = (r_att.status_code == 422 and r_cgpa.status_code == 422)
    results.append(("emergency == standard (both attendance & CGPA)", passed, (r_att.status_code, r_cgpa.status_code)))
    print(f"[{'PASS' if passed else 'FAIL'}] emergency == standard: status {r_att.status_code}, {r_cgpa.status_code}")

    # 7. emergency > standard (attendance & CGPA)
    r_att_gt = client.put("/api/v1/config/thresholds", json={"attendance_emergency_min": 85.0, "attendance_standard_min": 70.0})
    r_cgpa_gt = client.put("/api/v1/config/thresholds", json={"cgpa_emergency_min": 7.5, "cgpa_warning_min": 6.0})
    passed = (r_att_gt.status_code == 422 and r_cgpa_gt.status_code == 422)
    results.append(("emergency > standard (both attendance & CGPA)", passed, (r_att_gt.status_code, r_cgpa_gt.status_code)))
    print(f"[{'PASS' if passed else 'FAIL'}] emergency > standard: status {r_att_gt.status_code}, {r_cgpa_gt.status_code}")

    # 8. Backlog boundaries:
    # 8A: backlog_warning_max = 0, backlog_emergency_max = 0 (equality allowed)
    r_bl_eq = client.put("/api/v1/config/thresholds", json={"backlog_warning_max": 0, "backlog_emergency_max": 0})
    passed_bl_eq = (r_bl_eq.status_code == 200 and r_bl_eq.json()["thresholds"]["backlog_warning_max"] == 0)
    results.append(("backlog warning == emergency (0, 0)", passed_bl_eq, r_bl_eq.status_code))
    print(f"[{'PASS' if passed_bl_eq else 'FAIL'}] backlog warning == emergency (0, 0): status {r_bl_eq.status_code}")

    # 8B: backlog_warning_max > backlog_emergency_max (e.g. 5 > 3) -> 422
    r_bl_gt = client.put("/api/v1/config/thresholds", json={"backlog_warning_max": 5, "backlog_emergency_max": 3})
    passed_bl_gt = (r_bl_gt.status_code == 422)
    results.append(("backlog warning > emergency (5 > 3)", passed_bl_gt, r_bl_gt.status_code))
    print(f"[{'PASS' if passed_bl_gt else 'FAIL'}] backlog warning > emergency (5 > 3): status {r_bl_gt.status_code}")

    # 8C: backlog < 0 or > 20 -> 422
    r_bl_neg = client.put("/api/v1/config/thresholds", json={"backlog_warning_max": -1})
    r_bl_high = client.put("/api/v1/config/thresholds", json={"backlog_emergency_max": 25})
    passed_bl_bounds = (r_bl_neg.status_code == 422 and r_bl_high.status_code == 422)
    results.append(("backlog out of bounds (-1, 25)", passed_bl_bounds, (r_bl_neg.status_code, r_bl_high.status_code)))
    print(f"[{'PASS' if passed_bl_bounds else 'FAIL'}] backlog out of bounds (-1, 25): status {r_bl_neg.status_code}, {r_bl_high.status_code}")

    # Reset clean
    client.post("/api/v1/config/thresholds/reset")

    all_passed = all(r[1] for r in results)
    print(f"\n--- Boundary Extremes Summary: {sum(1 for r in results if r[1])}/{len(results)} Passed ---")
    assert all_passed, "Boundary extremes tests failed!"
    return results


def test_rate_limiting_enforcement():
    print("\n" + "=" * 80)
    print("TEST SUITE 2A: ADVERSARIAL RATE LIMITING ENFORCEMENT")
    print("=" * 80)

    RATE_LIMIT_STORE.clear()
    original_limit = api_main.RATE_LIMIT_MAX_PER_MINUTE
    api_main.RATE_LIMIT_MAX_PER_MINUTE = 120

    print("Sending 120 valid requests up to rate limit threshold...")
    for i in range(120):
        res = client.get("/api/v1/config/thresholds")
        assert res.status_code == 200, f"Request {i} unexpectedly failed"

    print("Sending 121st request to verify HTTP 429 RATE_LIMIT_EXCEEDED...")
    res_429 = client.get("/api/v1/config/thresholds")
    assert res_429.status_code == 429, f"Expected 429, got {res_429.status_code}"
    body = res_429.json()
    assert body["error"]["code"] == "RATE_LIMIT_EXCEEDED", f"Unexpected error code: {body}"
    assert res_429.headers.get("Retry-After") == "60"
    print(f"[PASS] Rate limiter correctly defended endpoint with HTTP 429 ({body['error']['code']})")

    # Clean up
    RATE_LIMIT_STORE.clear()
    api_main.RATE_LIMIT_MAX_PER_MINUTE = original_limit


def test_concurrency_and_repeated_resets():
    print("\n" + "=" * 80)
    print("TEST SUITE 2B: CONCURRENCY & REPEATED RESETS (/api/v1/config/thresholds)")
    print("=" * 80)

    # Relax rate limit temporarily for concurrent load testing
    RATE_LIMIT_STORE.clear()
    original_limit = api_main.RATE_LIMIT_MAX_PER_MINUTE
    api_main.RATE_LIMIT_MAX_PER_MINUTE = 20000

    # Reset initially
    client.post("/api/v1/config/thresholds/reset")

    total_ops = 500
    concurrency = 16
    print(f"Launching {total_ops} concurrent operations across {concurrency} worker threads...")

    operations = ["GET", "PUT_VALID", "PUT_INVALID", "RESET"]
    weights = [0.40, 0.30, 0.15, 0.15]

    stats = {
        "GET_200": 0,
        "PUT_VALID_200": 0,
        "PUT_INVALID_422": 0,
        "RESET_200": 0,
        "ERRORS_500": 0,
        "OTHER": 0,
    }

    def execute_single_op(idx: int):
        op = random.choices(operations, weights=weights)[0]
        if op == "GET":
            resp = client.get("/api/v1/config/thresholds")
            return ("GET", resp.status_code)
        elif op == "PUT_VALID":
            std = round(random.uniform(70.0, 95.0), 2)
            emg = round(random.uniform(40.0, std - 1.0), 2)
            resp = client.put("/api/v1/config/thresholds", json={
                "attendance_standard_min": std,
                "attendance_emergency_min": emg,
            })
            return ("PUT_VALID", resp.status_code)
        elif op == "PUT_INVALID":
            # deliberately invalid: emerg > std
            resp = client.put("/api/v1/config/thresholds", json={
                "attendance_standard_min": 60.0,
                "attendance_emergency_min": 85.0,
            })
            return ("PUT_INVALID", resp.status_code)
        elif op == "RESET":
            resp = client.post("/api/v1/config/thresholds/reset")
            return ("RESET", resp.status_code)

    t0 = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(execute_single_op, i) for i in range(total_ops)]
        for f in concurrent.futures.as_completed(futures):
            op, status = f.result()
            if op == "GET" and status == 200:
                stats["GET_200"] += 1
            elif op == "PUT_VALID" and status == 200:
                stats["PUT_VALID_200"] += 1
            elif op == "PUT_INVALID" and status == 422:
                stats["PUT_INVALID_422"] += 1
            elif op == "RESET" and status == 200:
                stats["RESET_200"] += 1
            elif status >= 500:
                stats["ERRORS_500"] += 1
            else:
                stats["OTHER"] += 1

    elapsed = time.time() - t0
    ops_per_sec = total_ops / elapsed
    print(f"Completed {total_ops} operations in {elapsed:.3f}s ({ops_per_sec:.1f} ops/sec)")
    print(f"Stats: {stats}")

    assert stats["ERRORS_500"] == 0, f"Found {stats['ERRORS_500']} 500 Internal Server Errors under concurrency!"
    assert stats["OTHER"] == 0, f"Unexpected non-200/422 responses: {stats['OTHER']}"

    # Final post-concurrency invariant verification
    reset_resp = client.post("/api/v1/config/thresholds/reset")
    assert reset_resp.status_code == 200, "Reset failed after concurrency"

    get_resp = client.get("/api/v1/config/thresholds")
    assert get_resp.status_code == 200
    final_data = get_resp.json()

    assert final_data["attendance_standard_min"] == 75.0, "Attendance standard corrupted"
    assert final_data["attendance_emergency_min"] == 57.0, "Attendance emergency corrupted"
    assert final_data["cgpa_warning_min"] == 6.0, "CGPA warning corrupted"
    assert final_data["cgpa_emergency_min"] == 4.7, "CGPA emergency corrupted"
    assert final_data["backlog_warning_max"] == 2, "Backlog warning corrupted"
    assert final_data["backlog_emergency_max"] == 3, "Backlog emergency corrupted"

    print("Post-concurrency state successfully restored to exact canonical defaults.")
    print("--- Concurrency & Repeated Resets PASSED ---")

    # Restore rate limit configuration
    RATE_LIMIT_STORE.clear()
    api_main.RATE_LIMIT_MAX_PER_MINUTE = original_limit
    return stats


def test_deterministic_scoring_100_iterations():
    print("\n" + "=" * 80)
    print("TEST SUITE 3: DETERMINISTIC SCORING REPRODUCIBILITY (100 ITERATIONS)")
    print("=" * 80)

    # Relax rate limit temporarily for 100 rapid API iterations
    RATE_LIMIT_STORE.clear()
    original_limit = api_main.RATE_LIMIT_MAX_PER_MINUTE
    api_main.RATE_LIMIT_MAX_PER_MINUTE = 20000

    # 1. Pure Domain Scoring on Synthetic Cohort
    print("Step 3A: Evaluating pure domain scoring on 50 synthetic students over 100 iterations...")
    rng = random.Random(42)  # Fixed seed for profile generation
    synthetic_students = []
    for i in range(50):
        student = {
            "id": f"SYNTH_{i:03d}",
            "cgpa": round(rng.uniform(3.5, 9.8), 2),
            "backlogs": rng.randint(0, 6),
            "attendance": round(rng.uniform(45.0, 99.0), 1),
            "subjects_below_60": rng.randint(0, 4),
            "aptitude": round(rng.uniform(30.0, 95.0), 1),
            "coding": round(rng.uniform(20.0, 100.0), 1),
            "mock": round(rng.uniform(25.0, 90.0), 1),
            "assignment_completion": round(rng.uniform(40.0, 100.0), 1),
            "scaled_logins": round(rng.uniform(30.0, 100.0), 1),
            "events": rng.randint(0, 5),
            "clubs": rng.randint(0, 3),
            "hackathons": rng.randint(0, 4),
            "certs": rng.randint(0, 3),
            "technical": round(rng.uniform(30.0, 95.0), 1),
            "soft": round(rng.uniform(40.0, 90.0), 1),
            "history": [round(rng.uniform(50.0, 80.0), 1) for _ in range(4)],
        }
        synthetic_students.append(student)

    cohort_p25 = {"attendance": 65.0, "lms": 50.0, "engagement": 25.0}

    domain_hashes = set()
    for iteration in range(100):
        iteration_results = []
        for s in synthetic_students:
            acad = compute_academic_index(s["cgpa"], s["backlogs"])
            att = compute_attendance_index(s["attendance"], s["subjects_below_60"])
            plc = compute_placement_index(s["aptitude"], s["coding"], s["mock"])
            lms = compute_lms_index(s["assignment_completion"], s["scaled_logins"])
            eng = compute_engagement_index(s["events"], s["clubs"], s["hackathons"], s["certs"])
            skl = compute_skills_index(s["technical"], s["soft"])
            score = compute_success_score(acad, att, plc, lms, eng, skl)

            tier, hard_floor = determine_tier(s["attendance"], s["cgpa"], s["backlogs"], score)
            momentum, delta = classify_momentum(s["history"])
            sub_indices = {"attendance": att, "lms": lms, "engagement": eng}
            priority = compute_priority_score(score, tier, hard_floor, momentum, sub_indices, cohort_p25)

            iteration_results.append({
                "id": s["id"],
                "acad": acad,
                "att": att,
                "plc": plc,
                "lms": lms,
                "eng": eng,
                "skl": skl,
                "score": score,
                "tier": tier.value,
                "hard_floor": hard_floor,
                "momentum": momentum.value,
                "delta": delta,
                "priority": priority,
            })

        # Serialize deterministically and compute SHA-256
        serialized = json.dumps(iteration_results, sort_keys=True)
        h = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        domain_hashes.add(h)

    print(f"Domain scoring 100 iterations complete. Unique SHA-256 digests: {len(domain_hashes)}")
    assert len(domain_hashes) == 1, f"Domain scoring is non-deterministic! Found {len(domain_hashes)} distinct hashes."
    domain_hash = list(domain_hashes)[0]
    print(f"Deterministic SHA-256 Digest: {domain_hash} (100/100 identical runs)")

    # 2. End-to-End API Action-List Determinism
    print("\nStep 3B: Evaluating API action-list endpoint over 100 rapid repeated calls...")
    api_hashes = set()
    auth_headers = {"X-User-Role": "admin", "X-User-Email": "admin@campuspulse.edu"}
    client.post("/api/v1/config/thresholds/reset")

    sample_student_ref = None

    for i in range(100):
        resp = client.get("/api/v1/advisors/me/action-list", headers=auth_headers)
        assert resp.status_code == 200, f"API failed on iteration {i}"
        data = resp.json().get("data", {})
        action_list = data.get("action_list", [])
        assert len(action_list) > 0, "Action list must contain student records"

        if sample_student_ref is None:
            sample_student_ref = action_list[0]["student_ref"]

        # Extract deterministic student scoring snapshot (excluding server timestamps or dynamic tokens)
        students_snapshot = []
        for item in action_list:
            students_snapshot.append({
                "student_ref": item.get("student_ref"),
                "name": item.get("name"),
                "success_score": item.get("success_score"),
                "tier": item.get("tier"),
                "priority_score": item.get("priority_score"),
                "hard_floor_breach": item.get("emergency_hard_floor_breach"),
                "standard_alert": item.get("standard_attendance_alert"),
                "sub_indices": item.get("sub_indices"),
            })

        snapshot_bytes = json.dumps(students_snapshot, sort_keys=True).encode("utf-8")
        h = hashlib.sha256(snapshot_bytes).hexdigest()
        api_hashes.add(h)

    print(f"API action-list 100 iterations complete. Unique SHA-256 digests: {len(api_hashes)}")
    assert len(api_hashes) == 1, f"API scoring is non-deterministic! Found {len(api_hashes)} distinct hashes."
    api_hash = list(api_hashes)[0]
    print(f"Deterministic API Digest: {api_hash} (100/100 identical runs)")

    # 3. Student Explain AST Audit Endpoint Determinism
    print(f"\nStep 3C: Evaluating student explain AST endpoint ({sample_student_ref}) over 100 rapid repeated calls...")
    explain_hashes = set()
    for i in range(100):
        resp = client.get(f"/api/v1/students/{sample_student_ref}/explain", headers=auth_headers)
        assert resp.status_code == 200, f"Explain endpoint failed on iteration {i}"
        data = resp.json().get("data", {})
        audit = data.get("audit", {})
        explain_snapshot = {
            "scoring_engine": audit.get("scoring_engine"),
            "ml_role": audit.get("ml_role"),
            "formula": audit.get("formula"),
            "success_score": data.get("success_score"),
            "tier": data.get("tier"),
            "active_thresholds": audit.get("thresholds"),
            "contributions": data.get("contributions"),
        }
        h = hashlib.sha256(json.dumps(explain_snapshot, sort_keys=True).encode("utf-8")).hexdigest()
        explain_hashes.add(h)

    print(f"Student explain AST 100 iterations complete. Unique SHA-256 digests: {len(explain_hashes)}")
    assert len(explain_hashes) == 1, f"Explain endpoint non-deterministic! Found {len(explain_hashes)} distinct hashes."
    explain_hash = list(explain_hashes)[0]
    print(f"Deterministic Explain Digest: {explain_hash} (100/100 identical runs)")
    print("--- Deterministic Scoring Reproducibility PASSED ---")

    # Restore rate limit
    RATE_LIMIT_STORE.clear()
    api_main.RATE_LIMIT_MAX_PER_MINUTE = original_limit

    return {
        "domain_hash": domain_hash,
        "api_hash": api_hash,
        "explain_hash": explain_hash,
        "iterations": 100,
        "variance": 0.000,
    }


def main():
    print("================================================================================")
    print("STARTING MILENSTONE 4 ADVERSARIAL STRESS TEST HARNESS")
    print("================================================================================")

    t_start = time.time()

    b_results = test_boundary_extremes()
    test_rate_limiting_enforcement()
    c_stats = test_concurrency_and_repeated_resets()
    d_results = test_deterministic_scoring_100_iterations()

    total_time = time.time() - t_start

    print("\n" + "=" * 80)
    print("OVERALL ADVERSARIAL STRESS TEST RESULTS: ALL SUITES PASSED!")
    print(f"Total Elapsed Time: {total_time:.2f}s")
    print("=" * 80)


if __name__ == "__main__":
    main()
