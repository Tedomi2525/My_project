from pydantic import BaseModel
from datetime import datetime

class ClassroomMemberBase(BaseModel):
    class_id: int
    student_id: int
    joined_at: datetime

    class Config:
        from_attributes = True