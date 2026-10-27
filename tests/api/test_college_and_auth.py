import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_college_login_activity_endpoint():
    response = client.get("/api/v1/cohorts/login-activity")
    assert response.status_code == 200
    json_data = response.json()
    assert "data" in json_data
    data = json_data["data"]
    assert data["total_students"] == 469
    assert data["total_batches"] == 7
    assert data["total_branches"] == 1
    assert data["total_educators"] == 2
    assert "inactive_alert" in data
    assert len(data["recent_active_students"]) > 0


def test_college_telemetry_endpoint():
    response = client.get("/api/v1/college/telemetry")
    assert response.status_code == 200
    json_data = response.json()
    assert "data" in json_data
    d = json_data["data"]
    assert "editor" in d
    assert "nimbus" in d
    assert "labs" in d
    assert "assessments" in d
    assert "courses" in d
    assert "leaderboard" in d
    assert "live" in d
    assert "video" in d


def test_project_bank_branding_clean():
    response = client.get("/api/v1/projects/bank")
    assert response.status_code == 200
    json_data = response.json()
    projects = json_data["data"]
    for p in projects:
        assert "byteXL" not in p.get("partner", ""), f"Leftover byteXL in partner: {p}"


def test_admin_department_faculty_hierarchy():
    response = client.get("/api/v1/admin/department-faculty")
    assert response.status_code == 200
    json_data = response.json()
    assert "data" in json_data
    d = json_data["data"]

    # Verify Dean (Superadmin)
    assert "dean" in d
    assert d["dean"]["name"] == "Prof. Rajesh Gupta"
    assert "Superadmin" in d["dean"]["role"]

    # Verify HOD (Admin)
    assert "hod" in d
    assert d["hod"]["name"] == "Dr. S. K. Venkatraman"
    assert "Admin" in d["hod"]["role"]
    assert d["hod"]["total_students"] == 469
    assert d["hod"]["total_faculty"] >= 4

    # Verify Teachers (Faculty) with assigned students under them
    assert "teachers" in d
    assert len(d["teachers"]) >= 4
    ananya = next((t for t in d["teachers"] if "Ananya" in t["name"]), None)
    assert ananya is not None
    assert ananya["assigned_students"] > 0
    assert any("Aarav" in m for m in ananya["key_mentees"])

    # Verify RBAC policies
    assert "rbac_policies" in d
    policies = {p["role"]: p for p in d["rbac_policies"]}
    assert "Full Access" in policies["Dean (Superadmin)"]["admin_portal"]
    assert "Full Access" in policies["HOD (Admin)"]["admin_portal"]
    assert "No Access (Hidden)" in policies["Teacher (Faculty)"]["admin_portal"]
    assert "No Access (Hidden)" in policies["Student"]["admin_portal"]


def test_capstone_project_assignment_and_allocation():
    # Test assigning/enrolling in a project
    res = client.post("/api/v1/projects/assign", json={
        "project_id": "proj-01",
        "student_name": "Priyanshu Pandey",
        "mentor_name": "Dr. Ananya Sharma",
        "notes": "Milestone 1 Architecture"
    })
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["assigned_to"] == "Priyanshu Pandey"
    assert "Priyanshu Pandey" in data["all_assigned"]


def test_capstone_faculty_document_management():
    # Test fetching initial documents
    res = client.get("/api/v1/projects/documents")
    assert res.status_code == 200
    docs = res.json()["data"]
    assert len(docs) >= 3
    assert any(d["file_type"] == "PDF" for d in docs)

    # Test uploading a new faculty document
    upload_res = client.post("/api/v1/projects/documents", json={
        "title": "NEP_2020_Evaluation_Rubric_v2.pdf",
        "project_id": "proj-01",
        "project_title": "Smart Campus Student-Success & Placement Intelligence OS",
        "uploaded_by": "Dr. Ananya Sharma",
        "uploaded_role": "Faculty Mentor",
        "size": "2.1 MB",
        "file_type": "PDF"
    })
    assert upload_res.status_code == 200
    new_doc = upload_res.json()["data"]
    assert new_doc["title"] == "NEP_2020_Evaluation_Rubric_v2.pdf"
    assert new_doc["uploaded_by"] == "Dr. Ananya Sharma"

    # Test deleting the document
    del_res = client.delete(f"/api/v1/projects/documents/{new_doc['id']}")
    assert del_res.status_code == 200


def test_kpmg_deliverables_and_segmentation_matrix():
    # Test KPMG Challenge Deliverables endpoint
    deliv_res = client.get("/api/v1/kpmg/deliverables")
    assert deliv_res.status_code == 200
    data = deliv_res.json()["data"]
    assert "pitch_deck" in data
    assert "evaluation_rubric_mapping" in data
    assert "data_integration" in data
    assert len(data["pitch_deck"]) >= 5

    # Test KPMG 2D Student Segmentation Matrix endpoint
    seg_res = client.get("/api/v1/kpmg/segmentation-matrix")
    assert seg_res.status_code == 200
    seg_data = seg_res.json()["data"]
    assert "students" in seg_data
    assert "quadrant_distribution" in seg_data
    assert "cohort_benchmarks" in seg_data
    assert isinstance(seg_data["students"], list)



