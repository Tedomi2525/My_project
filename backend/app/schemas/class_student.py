from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ClassStudentBase(BaseModel):
    class_id: int
    student_id: int

class ClassStudentCreate(ClassStudentBase):
    pass

class ClassStudentResponse(ClassStudentBase):
    id: int
    joined_at: Optional[datetime]

    class Config:
        from_attributes = True