from pydantic import BaseModel
from datetime import datetime

# -------- Student info trả về cho frontend --------
class StudentResponse(BaseModel):
    id: int
    full_name: str
    email: str

    class Config:
        from_attributes = True


# -------- Base --------
class ClassStudentBase(BaseModel):
    class_id: int
    student_id: int


# -------- Create --------
class ClassStudentCreate(ClassStudentBase):
    pass


# -------- Response --------
class ClassStudentResponse(BaseModel):
    id: int
    joined_at: datetime
    student: StudentResponse

    class Config:
        from_attributes = True
