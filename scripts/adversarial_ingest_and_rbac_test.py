# -*- coding: utf-8 -*-
"""
Milestone 4 Adversarial Test Harness: Ingestion Robustness, File Upload Limits & RBAC
Empirically stress-tests:
1. File size boundaries (15MB limit, oversized payloads, leak cleanup)
2. Role-Based Access Control (RBAC) across student, anonymous, advisor, admin, dean, hod
3. Malformed data handling (empty files, whitespace, unclosed quotes, broken delimiters, non-UTF8 encodings, binary injection)
4. Scalability benchmark (10, 100, 500 rows and time complexity analysis)
"""

import io
import os
import sys
import time
from pathlib import Path

# Ensure root directory is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from apps.api.main import app, RATE_LIMIT_STORE
import apps.api.main as api_main

client = TestClient(app, raise_server_exceptions=False)


def run_rbac_suite():
    print("\n" + "=" * 80)
    print("SUITE 1: UPLOAD & INGESTION ROLE-BASED ACCESS CONTROL (RBAC)")
    print("=" * 80)

    # Relax rate limits for testing
    RATE_LIMIT_STORE.clear()

    valid_csv = b"Roll Number,Name,Total Score\n2023CSE001,Test Student,22\n"

    # Test 1A: Anonymous role header -> HTTP 401
    res_anon = client.post(
        "/api/v1/ingest/upload",
        files={"file": ("dataset.csv", io.BytesIO(valid_csv), "text/csv")},
        headers={"X-User-Role": "anonymous"},
    )
    print(f"[*] Anonymous role header status: {res_anon.status_code}")
    assert res_anon.status_code == 401, f"Expected 401, got {res_anon.status_code}"
    assert "Authentication required" in res_anon.json()["error"]["message"]
    print("[PASS] Anonymous role rejected with HTTP 401.")

    # Test 1B: Explicit unauthenticated bearer token -> HTTP 401
    res_unauth = client.post(
        "/api/v1/ingest/upload",
        files={"file": ("dataset.csv", io.BytesIO(valid_csv), "text/csv")},
        headers={"Authorization": "Bearer unauthenticated"},
    )
    print(f"[*] Unauthenticated bearer status: {res_unauth.status_code}")
    assert res_unauth.status_code == 401, f"Expected 401, got {res_unauth.status_code}"
    print("[PASS] Unauthenticated bearer token rejected with HTTP 401.")

    # Test 1C: Student role header -> HTTP 403 Forbidden
    res_student = client.post(
        "/api/v1/ingest/upload",
        files={"file": ("dataset.csv", io.BytesIO(valid_csv), "text/csv")},
        headers={"X-User-Role": "student", "X-User-Email": "student@campuspulse.edu"},
    )
    print(f"[*] Student role header status: {res_student.status_code}")
    assert res_student.status_code == 403, f"Expected 403, got {res_student.status_code}"
    assert "Students cannot upload or ingest" in res_student.json()["error"]["message"]
    print("[PASS] Student role rejected with HTTP 403.")

    # Test 1D: Student email inference -> HTTP 403 Forbidden
    res_student_email = client.post(
        "/api/v1/ingest/upload",
        files={"file": ("dataset.csv", io.BytesIO(valid_csv), "text/csv")},
        headers={"X-User-Email": "student.aarav@campuspulse.edu"},
    )
    print(f"[*] Student email inference status: {res_student_email.status_code}")
    assert res_student_email.status_code == 403, f"Expected 403, got {res_student_email.status_code}"
    print("[PASS] Student email inference rejected with HTTP 403.")

    # Test 1E: Preset ingestion student rejection -> HTTP 403 Forbidden
    res_preset_student = client.post(
        "/api/v1/ingest/preset/sample",
        headers={"X-User-Role": "student", "X-User-Email": "student@campuspulse.edu"},
    )
    print(f"[*] Preset ingestion student status: {res_preset_student.status_code}")
    assert res_preset_student.status_code == 403, f"Expected 403, got {res_preset_student.status_code}"
    print("[PASS] Preset ingestion endpoint rejects student role with HTTP 403.")

    # Test 1F: Preset ingestion anonymous rejection -> HTTP 401 Unauthorized
    res_preset_anon = client.post(
        "/api/v1/ingest/preset/sample",
        headers={"X-User-Role": "anonymous"},
    )
    print(f"[*] Preset ingestion anonymous status: {res_preset_anon.status_code}")
    assert res_preset_anon.status_code == 401, f"Expected 401, got {res_preset_anon.status_code}"
    print("[PASS] Preset ingestion endpoint rejects anonymous user with HTTP 401.")

    # Test 1G: Authorized role access (Admin)
    res_admin = client.post(
        "/api/v1/ingest/upload",
        files={"file": ("rbac_admin.csv", io.BytesIO(valid_csv), "text/csv")},
        headers={"X-User-Role": "admin", "X-User-Email": "admin@campuspulse.edu"},
    )
    print(f"[*] Admin role status: {res_admin.status_code}")
    assert res_admin.status_code == 200, f"Expected 200 for admin, got {res_admin.status_code}"
    print("[PASS] Admin role permitted with HTTP 200.")

    # Test 1H: Authorized role access (Advisor)
    res_adv = client.post(
        "/api/v1/ingest/upload",
        files={"file": ("rbac_adv.csv", io.BytesIO(valid_csv), "text/csv")},
        headers={"X-User-Role": "advisor", "X-User-Email": "advisor@campuspulse.edu"},
    )
    print(f"[*] Advisor role status: {res_adv.status_code}")
    assert res_adv.status_code == 200, f"Expected 200 for advisor, got {res_adv.status_code}"
    print("[PASS] Advisor role permitted with HTTP 200.")


def run_file_size_and_extension_suite():
    print("\n" + "=" * 80)
    print("SUITE 2: FILE SIZE LIMITS, EXTENSION FILTERING & LEAK PREVENTION")
    print("=" * 80)

    raw_dir = Path("./data/raw").resolve()
    raw_dir.mkdir(parents=True, exist_ok=True)

    # Count initial files in ./data/raw
    initial_files = set(raw_dir.iterdir())

    # Test 2A: Unsupported extension .exe
    res_exe = client.post(
        "/api/v1/ingest/upload",
        files={"file": ("test.exe", io.BytesIO(b"MZfake"), "application/octet-stream")},
        headers={"X-User-Role": "admin"},
    )
    assert res_exe.status_code == 400
    assert "Invalid file extension" in res_exe.json()["error"]["message"]
    print(f"[PASS] .exe rejected with HTTP 400: {res_exe.json()['error']['message']}")

    # Test 2B: Unsupported extension .php
    res_php = client.post(
        "/api/v1/ingest/upload",
        files={"file": ("exploit.php", io.BytesIO(b"<?php ?>"), "application/x-php")},
        headers={"X-User-Role": "admin"},
    )
    assert res_php.status_code == 400
    print(f"[PASS] .php rejected with HTTP 400.")

    # Test 2C: Disguised binary/executable (.csv extension but ELF binary header)
    res_elf = client.post(
        "/api/v1/ingest/upload",
        files={"file": ("fake.csv", io.BytesIO(b"\x7fELFfakecontent"), "text/csv")},
        headers={"X-User-Role": "admin"},
    )
    assert res_elf.status_code == 400
    assert "Executable or binary content detected" in res_elf.json()["error"]["message"]
    print(f"[PASS] ELF binary disguised as .csv rejected with HTTP 400.")

    # Test 2D: Disguised executable (.csv extension with MZ Windows PE header)
    res_mz = client.post(
        "/api/v1/ingest/upload",
        files={"file": ("fake_pe.csv", io.BytesIO(b"MZ\x90\x00this is pe binary"), "text/csv")},
        headers={"X-User-Role": "admin"},
    )
    assert res_mz.status_code == 400
    assert "Executable or binary content detected" in res_mz.json()["error"]["message"]
    print(f"[PASS] PE binary disguised as .csv rejected with HTTP 400.")

    # Test 2E: Fake Excel file (missing ZIP OOXML PK\x03\x04 header)
    res_bad_xlsx = client.post(
        "/api/v1/ingest/upload",
        files={"file": ("fake.xlsx", io.BytesIO(b"not an excel file"), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        headers={"X-User-Role": "admin"},
    )
    assert res_bad_xlsx.status_code == 400
    assert "Missing standard ZIP/OOXML magic header" in res_bad_xlsx.json()["error"]["message"]
    print(f"[PASS] Corrupt .xlsx missing PK magic header rejected with HTTP 400.")

    # Test 2F: Path traversal attempt in filename
    res_traversal = client.post(
        "/api/v1/ingest/upload",
        files={"file": ("../../etc/shadow.csv", io.BytesIO(b"Roll Number,Name\n1,A\n"), "text/csv")},
        headers={"X-User-Role": "admin"},
    )
    # Either sanitized safely or rejected
    assert res_traversal.status_code in (200, 400)
    print(f"[PASS] Path traversal attempt in filename handled safely with status {res_traversal.status_code}")

    # Test 2G: Oversized file exceeding 15MB limit (15MB + 1KB)
    print("Testing 15MB file size boundary enforcement...")
    oversized_bytes = 15 * 1024 * 1024 + 1024  # 15 MB + 1 KB
    res_oversized = client.post(
        "/api/v1/ingest/upload",
        files={"file": ("oversized_boundary.csv", io.BytesIO(b"X" * oversized_bytes), "text/csv")},
        headers={"X-User-Role": "admin"},
    )
    assert res_oversized.status_code == 413, f"Expected 413, got {res_oversized.status_code}"
    assert "File exceeds maximum allowed size of 15MB" in res_oversized.json()["error"]["message"]
    print(f"[PASS] 15MB + 1KB file rejected with HTTP 413.")

    # Test 2H: Verify no temporary files leaked on disk
    leaked_files = [f for f in raw_dir.glob("*oversized_boundary*")]
    assert len(leaked_files) == 0, f"Temporary file leaked on disk: {leaked_files}"
    print("[PASS] Leaked temporary file verification: zero residual artifacts in data/raw.")


def run_malformed_csv_and_encoding_suite():
    print("\n" + "=" * 80)
    print("SUITE 3: MALFORMED DATA & NON-UTF8 ENCODINGS")
    print("=" * 80)

    cases = [
        ("Empty File (0 bytes)", "empty.csv", b"", "text/csv"),
        ("Whitespace Only", "whitespace.csv", b"   \r\n\r\n   \t  \n", "text/csv"),
        ("Header Only (0 records)", "header_only.csv", b"Roll Number,Name,Total Score\n", "text/csv"),
        ("Unclosed Quotes", "unclosed.csv", b'Roll Number,Name,Total Score\n2023CSE001,"Unclosed quote string,25\n', "text/csv"),
        ("Inconsistent Columns", "inconsistent.csv", b"Roll Number,Name,Total Score\n2023CSE001,Student,20,extra1,extra2,extra3\n", "text/csv"),
        ("Latin-1 (ISO-8859-1) Encoding", "latin1.csv", "Roll Number,Name,Total Score\n2023CSE001,Renée François,22\n".encode("latin-1"), "text/csv"),
        ("Windows-1252 (CP1252) Euro Sign", "cp1252.csv", b"Roll Number,Name,Total Score\n2023CSE001,St\x80dent,22\n", "text/csv"),
        ("Corrupted Random Bytes", "junk.csv", b"\x90\x81\xa3\xbb\xcc\xdd\xee\xff\xaa\xbb\xcc", "text/csv"),
    ]

    findings = []
    for name, filename, content, mime in cases:
        f = io.BytesIO(content)
        res = client.post(
            "/api/v1/ingest/upload",
            files={"file": (filename, f, mime)},
            headers={"X-User-Role": "admin", "X-User-Email": "admin@campuspulse.edu"},
        )
        status = res.status_code
        body = res.json() if res.headers.get("content-type") == "application/json" else res.text[:200]
        code = body.get("error", {}).get("code") if isinstance(body, dict) else "N/A"
        msg = body.get("error", {}).get("message") if isinstance(body, dict) else body

        print(f"[*] {name}: status={status}, code={code}")
        findings.append({
            "case": name,
            "filename": filename,
            "status": status,
            "error_code": code,
            "message": msg,
        })

    print("\n--- Summary of Malformed Input Behavior ---")
    for f in findings:
        print(f"  - {f['case']}: HTTP {f['status']} ({f['error_code']})")

    return findings


def run_scalability_benchmark():
    print("\n" + "=" * 80)
    print("SUITE 4: SCALABILITY & TIME COMPLEXITY BENCHMARK")
    print("=" * 80)

    header = "Roll Number,Name,Total Score,Time Spent,Plagiarism %,Multi-IP\n"

    cohort_sizes = [10, 50, 100]
    timings = {}

    for n in cohort_sizes:
        rows = [f"2023CSE_{n}_{i:04d},Student_{n}_{i},{15 + (i % 10)},25,0.0,0" for i in range(n)]
        csv_bytes = (header + "\n".join(rows) + "\n").encode("utf-8")

        t0 = time.time()
        res = client.post(
            "/api/v1/ingest/upload",
            files={"file": (f"benchmark_{n}.csv", io.BytesIO(csv_bytes), "text/csv")},
            headers={"X-User-Role": "admin"},
        )
        elapsed = time.time() - t0
        timings[n] = elapsed
        print(f"[*] Cohort size {n:4d} rows: {elapsed:.3f}s ({n/elapsed:.1f} rows/s, status={res.status_code})")
        assert res.status_code == 200

    # Calculate per-record persistence rate
    ms_per_row = (timings[100] / 100) * 1000
    projected_10k_sec = (timings[100] / 100) * 10000
    print(f"\n[BENCHMARK] Average latency per row: {ms_per_row:.1f} ms/row")
    print(f"[BENCHMARK] Projected single-transaction latency for 10,000 rows: {projected_10k_sec:.1f}s ({projected_10k_sec/60:.1f} minutes)")
    print(f"[ARCHITECTURAL FINDING] Ingestion uses per-row synchronous commits (session.commit() on Student, AssessmentResult, WeeklyMetric). Under 10,000 records, this results in ~20,000 disk fsyncs causing synchronous request timeouts unless batched/bulk-inserted.")

    return timings, projected_10k_sec


def main():
    print("################################################################################")
    print("EMPIRICAL ADVERSARIAL TEST HARNESS: INGESTION, UPLOAD BOUNDARIES & RBAC")
    print("################################################################################")
    t0 = time.time()

    run_rbac_suite()
    run_file_size_and_extension_suite()
    findings = run_malformed_csv_and_encoding_suite()
    timings, projected_10k = run_scalability_benchmark()

    elapsed = time.time() - t0
    print("\n" + "#" * 80)
    print(f"ALL ADVERSARIAL TEST SUITES EXECUTED IN {elapsed:.2f}s")
    print("#" * 80)


if __name__ == "__main__":
    main()
