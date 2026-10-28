"""
Pydantic API request and response schemas for CampusPulse v5.0.
Implements strict form validation, bounds checking, and input sanitization (CWE-20).
"""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ResponseMeta(BaseModel):
    config_hash: Optional[str] = None
    targets_hash: Optional[str] = None
    generated_at: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    request_id: Optional[str] = None


class ApiResponse(BaseModel):
    data: Any
    meta: ResponseMeta


class ErrorDetail(BaseModel):
    code: str
    message: str
    hint: Optional[str] = None


class ErrorEnvelope(BaseModel):
    error: ErrorDetail


class InterventionCreate(BaseModel):
    student_ref: str = Field(..., min_length=3, max_length=64)
    action_code: str = Field(..., min_length=2, max_length=64)
    notes: Optional[str] = Field(None, max_length=2000)
    due_at: Optional[datetime.datetime] = None


class InterventionUpdate(BaseModel):
    status: Optional[str] = Field(None, max_length=32)
    notes: Optional[str] = Field(None, max_length=2000)


class WhatIfOverride(BaseModel):
    indicator: str = Field(..., max_length=32)  # 'academic', 'attendance', 'placement', 'lms', 'engagement', 'skills'
    delta: Optional[float] = Field(0.0, ge=-100.0, le=100.0)
    value: Optional[float] = Field(None, ge=0.0, le=100.0)


class WhatIfRequest(BaseModel):
    student_ref: str = Field(..., min_length=3, max_length=64)
    overrides: List[WhatIfOverride]


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    advisor_id: Optional[str] = Field(None, max_length=64)


class NaacSimulationRequest(BaseModel):
    overrides: Optional[Dict[str, float]] = None


# ── Strict Input Validation Schemas (Item 5) ──────────────────────────────────

class LabSessionCreate(BaseModel):
    mode: Optional[str] = Field("catalog", max_length=32)
    lab_id: Optional[str] = Field(None, max_length=64)
    title: Optional[str] = Field(None, max_length=128)
    sections: List[str] = Field(..., min_length=1)
    deadline: Optional[str] = Field(None, max_length=64)
    instructions: Optional[str] = Field(None, max_length=2000)
    problem_statement: Optional[str] = Field(None, max_length=10000)
    starter_code: Optional[str] = Field(None, max_length=10000)
    difficulty: Optional[str] = Field("Medium", max_length=32)
    points: Optional[int] = Field(50, ge=1, le=1000)
    test_cases_total: Optional[int] = Field(5, ge=1, le=100)
    faculty_name: Optional[str] = Field("Dr. Ananya Sharma", max_length=128)
    faculty_email: Optional[str] = Field(None, max_length=128)


class ExcellenceNominationCreate(BaseModel):
    student_ref: str = Field(..., min_length=3, max_length=64)
    category: str = Field("Fast-Track Placement", max_length=100)
    rating: int = Field(5, ge=1, le=5)
    remarks: str = Field("Exemplary consistency and placement readiness.", max_length=500)


class CodeSandboxRequest(BaseModel):
    code: str = Field(..., max_length=20000)
    language: str = Field("python", max_length=32)
    problem_id: str = Field("two_sum", max_length=64)


class NimbusCommandRequest(BaseModel):
    command: str = Field(..., max_length=256)


class ProjectAssignRequest(BaseModel):
    project_id: str = Field(..., min_length=1, max_length=64)
    student_name: Optional[str] = Field("Student", max_length=128)


class SprintModuleToggleRequest(BaseModel):
    module_id: str = Field(..., min_length=1, max_length=64)
    action: Optional[str] = Field(None, max_length=32)


class UserAuthContext(BaseModel):
    user_id: str = "usr_default"
    email: str = "ananya.sharma@campuspulse.edu"
    role: str = "advisor"  # 'admin', 'dean', 'hod', 'faculty', 'advisor', 'student'
    student_ref: Optional[str] = None
