from pydantic import BaseModel

class ExamResultDetailBase(BaseModel):
    result_id: int
    question_id: int
    student_answer: str

class ExamResultDetailCreate(ExamResultDetailBase):
    pass # is_correct sẽ do Server tự tính toán, Client không gửi lên

class ExamResultDetailResponse(ExamResultDetailBase):
    id: int
    is_correct: bool

    class Config:
        orm_mode = True 