from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel, Field


class ExamStartResponse(BaseModel):
    session_id: int
    exam_id: int
    student_id: int
    answers: Dict[str, str] = Field(default_factory=dict)
    violation_count: int = 0
    started_at: datetime | None = None
    last_saved_at: datetime | None = None

    class Config:
        from_attributes = True


class ExamAutosaveRequest(BaseModel):
    answers: Dict[str, str] = Field(default_factory=dict)


class ExamViolationRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=255)


class ExamViolationResponse(BaseModel):
    id: int
    session_id: int
    exam_id: int
    student_id: int
    reason: str
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class ExamSessionDetailResponse(ExamStartResponse):
    violations: List[ExamViolationResponse] = Field(default_factory=list)
