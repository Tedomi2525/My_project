from datetime import datetime

from pydantic import BaseModel


class ExamResultTeacherResponse(BaseModel):
    id: int
    exam_id: int
    student_id: int
    student_name: str
    student_code: str
    total_score: float
    started_at: datetime | None = None
    finished_at: datetime | None = None

