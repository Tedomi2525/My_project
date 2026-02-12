from pydantic import BaseModel

class ExamQuestionBase(BaseModel):
    exam_id: int
    question_id: int

class ExamQuestionCreate(ExamQuestionBase):
    pass

class ExamQuestionResponse(ExamQuestionBase):
    id: int

    class Config:
        from_attributes = True