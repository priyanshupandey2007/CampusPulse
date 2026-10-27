"""
Unit tests for NAAC & NEP 2020 domain scoring engine.
Verifies criteria weights, CGPA math, grade mapping, and NEP matrix integrity.
"""

import pytest
from packages.domain.naac import (
    NAAC_CRITERIA_WEIGHTS,
    INSTITUTION_METADATA,
    compute_live_naac_score,
    get_criteria_definitions,
    get_naac_grade,
    get_nep_matrix,
)


def test_naac_criteria_weights_sum_to_1000():
    """Validates NAAC RAF invariant: 7 criteria weights must sum to exactly 1000."""
    total_weight = sum(NAAC_CRITERIA_WEIGHTS.values())
    assert total_weight == 1000, f"Expected 1000, got {total_weight}"
    assert len(NAAC_CRITERIA_WEIGHTS) == 7


def test_naac_grade_mapping_thresholds():
    """Tests NAAC letter grade and maturity level thresholds."""
    grade, status, level = get_naac_grade(3.75)
    assert grade == "A++"
    assert "Level 4" in level

    grade, status, level = get_naac_grade(3.35)
    assert grade == "A+"
    assert "Level 3" in level

    grade, status, level = get_naac_grade(3.10)
    assert grade == "A"

    grade, status, level = get_naac_grade(2.80)
    assert grade == "B++"

    grade, status, level = get_naac_grade(2.60)
    assert grade == "B+"

    grade, status, level = get_naac_grade(2.20)
    assert grade == "B"

    grade, status, level = get_naac_grade(1.80)
    assert grade == "C"

    grade, status, level = get_naac_grade(1.20)
    assert grade == "D"
    assert "Unaccredited" in level


def test_compute_live_naac_score_baseline():
    """Tests baseline institutional score calculation without database session."""
    eval_result = compute_live_naac_score()
    assert eval_result["institution"]["short_name"] == "KRMU"
    assert eval_result["institution"]["aishe_code"] == "U-0162"
    assert 3.51 <= eval_result["cgpa"] <= 4.00
    assert eval_result["grade"] == "A++"
    assert len(eval_result["criteria"]) == 7
    assert eval_result["total_weight"] == 1000
    assert eval_result["nep_compliance_pct"] >= 90.0


def test_compute_live_naac_score_simulation_override():
    """Tests simulation overrides on criteria scores."""
    baseline = compute_live_naac_score()
    # Boost research criterion from 3.42 to 4.00
    simulated = compute_live_naac_score(overrides={"criterion_3": 4.00})
    assert simulated["cgpa"] >= baseline["cgpa"]
    for c in simulated["criteria"]:
        if c["key"] == "criterion_3":
            assert c["score"] == 4.00


def test_nep_matrix_integrity():
    """Tests NEP 2020 matrix contains all 8 institutional pillars."""
    nep = get_nep_matrix()
    assert nep["overall_compliance_pct"] >= 90.0
    assert len(nep["pillars"]) == 8
    pillar_ids = [p["id"] for p in nep["pillars"]]
    assert "nep_1" in pillar_ids
    assert "nep_5" in pillar_ids
    assert "nep_8" in pillar_ids


def test_batches_breakdown_and_swoc_integrity():
    """Validates institutional batch breakdown, student ABC ledger, and SWOC analysis."""
    eval_result = compute_live_naac_score()
    assert "batches_breakdown" in eval_result
    assert len(eval_result["batches_breakdown"]) == 7
    batch_names = [b["batch_name"] for b in eval_result["batches_breakdown"]]
    assert "KRMU_2029_AIML_E" in batch_names
    assert "KRMU_2029_CSE_C" in batch_names
    assert "KRMU_2029_CSE_D" in batch_names

    assert "sample_abc_ledger" in eval_result
    assert len(eval_result["sample_abc_ledger"]) >= 5
    first_student = eval_result["sample_abc_ledger"][0]
    assert "apaar_abc_id" in first_student
    assert "roll_number" in first_student
    assert "credits_earned" in first_student

    assert "swoc_analysis" in eval_result
    swoc = eval_result["swoc_analysis"]
    assert "strengths" in swoc and len(swoc["strengths"]) >= 4
    assert "weaknesses" in swoc and len(swoc["weaknesses"]) >= 3
    assert "opportunities" in swoc and len(swoc["opportunities"]) >= 3
    assert "challenges" in swoc and len(swoc["challenges"]) >= 3

