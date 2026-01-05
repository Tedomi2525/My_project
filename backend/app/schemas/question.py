from pydantic import BaseModel
from typing import Optional, Dict, Any

class QuestionBase(BaseModel):
    content: str
    question_type: Optional[str] = "MCQ"
    # Options nhận vào dict. VD: {"A": "Đáp án A", "B": "Đáp án B"}
    options: Optional[Dict[str, Any]] = None
    correct_answer: str

class QuestionCreate(QuestionBase):
    created_by: int

class QuestionResponse(QuestionBase):
    id: int
    created_by: int

    class Config:
        from_attributes = True