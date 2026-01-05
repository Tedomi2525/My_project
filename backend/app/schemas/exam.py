from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ExamBase(BaseModel):
    title: str
    description: Optional[str] = None
    duration_minutes: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class ExamCreate(ExamBase):
    created_by: int

class ExamResponse(ExamBase):
    id: int
    created_by: int

    class Config:
        from_attributes = True