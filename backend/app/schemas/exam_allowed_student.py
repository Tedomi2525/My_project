from pydantic import BaseModel

class ExamAllowedStudentBase(BaseModel):
    exam_id: int
    student_id: int

class ExamAllowedStudentCreate(ExamAllowedStudentBase):
    pass

class ExamAllowedStudentResponse(ExamAllowedStudentBase):
    id: int

    class Config:
        from_attributes = True