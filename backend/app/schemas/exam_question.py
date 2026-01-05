from pydantic import BaseModel

class ExamQuestionBase(BaseModel):
    exam_id: int
    question_id: int
    point: int = 1

class ExamQuestionCreate(ExamQuestionBase):
    pass

class ExamQuestionResponse(ExamQuestionBase):
    id: int

    class Config:
        from_attributes = True