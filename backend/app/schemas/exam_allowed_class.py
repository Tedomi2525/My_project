from pydantic import BaseModel

class ExamAllowedClassBase(BaseModel):
    exam_id: int
    class_id: int

class ExamAllowedClassCreate(ExamAllowedClassBase):
    pass

class ExamAllowedClassResponse(ExamAllowedClassBase):
    id: int

    class Config:
        from_attributes = True