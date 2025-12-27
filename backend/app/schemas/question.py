from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class QuestionBase(BaseModel):
    content: str
    image_url: Optional[str] = None
    option_a: str
    option_b: str
    option_c: Optional[str] = None
    option_d: Optional[str] = None
    correct_answer: str # 'A', 'B', 'C', 'D'

class QuestionCreate(QuestionBase):
    pass

class QuestionResponse(QuestionBase):
    question_id: int
    teacher_id: int
    created_at: datetime

    class Config:
        from_attributes = True