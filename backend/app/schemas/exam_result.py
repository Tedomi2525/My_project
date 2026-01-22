from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ExamResultBase(BaseModel):
    exam_id: int
    student_id: int

class ExamResultCreate(ExamResultBase):
    started_at: datetime

class ExamResultResponse(ExamResultBase):
    id: int
    total_score: float
    started_at: Optional[datetime]
    finished_at: Optional[datetime]

    class Config:
        orm_mode = True 