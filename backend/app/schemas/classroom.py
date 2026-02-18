from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ClassCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ClassUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class StudentInClassResponse(BaseModel):
    id: int
    full_name: str
    email: str
    joined_at: datetime


class ClassResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    teacher_id: int
    student_count: int = 0


class ClassDetailResponse(ClassResponse):
    students: List[StudentInClassResponse] = Field(default_factory=list)
