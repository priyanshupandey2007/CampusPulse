"""
API integration tests for NAAC Accreditation & NEP 2020 Platform endpoints.
Verifies response envelopes, status codes, simulation logic, and SSR generation.
"""

import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_naac_overview_endpoint():
    """Tests GET /api/v1/naac/overview returns full institutional evaluation envelope."""
    response = client.get("/api/v1/naac/overview")
    assert response.status_code == 200
    json_data = response.json()

    assert "data" in json_data
    assert "meta" in json_data
    d = json_data["data"]

    assert d["institution"]["institution_name"] == "K.R. Mangalam University"
    assert d["institution"]["aishe_code"] == "U-0162"
    assert d["cgpa"] >= 3.51
    assert d["grade"] == "A++"
    assert len(d["criteria"]) == 7
    assert "live_signals" in d
    assert "average_attendance" in d["live_signals"]
    assert "batches_breakdown" in d and len(d["batches_breakdown"]) == 7
    assert "sample_abc_ledger" in d and len(d["sample_abc_ledger"]) >= 5
    assert "swoc_analysis" in d and "strengths" in d["swoc_analysis"]



def test_naac_criteria_list_and_detail():
    """Tests GET /api/v1/naac/criteria and single criterion retrieval."""
    res_list = client.get("/api/v1/naac/criteria")
    assert res_list.status_code == 200
    d_list = res_list.json()["data"]
    assert len(d_list["criteria"]) == 7

    # Check Criterion 1 detail
    res_c1 = client.get("/api/v1/naac/criteria/1")
    assert res_c1.status_code == 200
    d_c1 = res_c1.json()["data"]
    assert d_c1["id"] == 1
    assert d_c1["name"] == "Curricular Aspects"
    assert len(d_c1["key_indicators"]) >= 4

    # Check Criterion 7 detail (Institutional Best Practices)
    res_c7 = client.get("/api/v1/naac/criteria/7")
    assert res_c7.status_code == 200
    d_c7 = res_c7.json()["data"]
    assert d_c7["id"] == 7
    assert any("CampusPulse" in ki["title"] for ki in d_c7["key_indicators"])

    # Invalid Criterion
    res_inv = client.get("/api/v1/naac/criteria/99")
    assert res_inv.status_code == 404


def test_naac_nep_matrix_endpoint():
    """Tests GET /api/v1/naac/nep-matrix returns 8 NEP pillars."""
    response = client.get("/api/v1/naac/nep-matrix")
    assert response.status_code == 200
    d = response.json()["data"]
    assert d["overall_compliance_pct"] >= 90.0
    assert len(d["pillars"]) == 8


def test_naac_simulate_endpoint():
    """Tests POST /api/v1/naac/simulate updates CGPA accurately."""
    payload = {
        "overrides": {
            "criterion_1": 4.00,
            "criterion_2": 4.00,
            "criterion_3": 4.00,
            "criterion_4": 4.00,
            "criterion_5": 4.00,
            "criterion_6": 4.00,
            "criterion_7": 4.00,
        }
    }
    response = client.post("/api/v1/naac/simulate", json=payload)
    assert response.status_code == 200
    d = response.json()["data"]
    assert d["cgpa"] == 4.00
    assert d["grade"] == "A++"


def test_naac_ssr_export_endpoint():
    """Tests GET /api/v1/naac/ssr-export generates executive SSR / AQAR dossier."""
    response = client.get("/api/v1/naac/ssr-export")
    assert response.status_code == 200
    d = response.json()["data"]

    assert "K.R. Mangalam University" in d["institution"]["institution_name"]
    assert len(d["criterion_summary_table"]) == 7
    assert len(d["institutional_best_practices"]) == 2
    assert "CampusPulse" in d["institutional_best_practices"][0]["title"]
    assert d["iqac_declaration"]["status"] == "APPROVED FOR PEER TEAM SUBMISSION"
