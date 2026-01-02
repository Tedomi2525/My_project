from pydantic import BaseModel
from typing import Optional

class ClassroomBase(BaseModel):
    class_name: str

class ClassroomCreate(ClassroomBase):
    pass

class ClassroomResponse(ClassroomBase):
    class_id: int
    teacher_id: int
    # Field này thường được tính toán khi query
    student_count: int = 0 
    
    class Config:
        from_attributes = True