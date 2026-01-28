from pydantic import BaseModel
from typing import Optional, Dict, Any
from enum import Enum

# 1. Định nghĩa Enum cho độ khó
class DifficultyLevel(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"

class QuestionBase(BaseModel):
    content: str
    question_type: Optional[str] = "MCQ"
    # 2. Thêm trường difficulty
    difficulty: DifficultyLevel = DifficultyLevel.EASY
    options: Optional[Dict[str, Any]] = None
    correct_answer: str

class QuestionCreate(QuestionBase):
    created_by: int

class QuestionResponse(QuestionBase):
    id: int
    created_by: int

    class Config:
        from_attributes = True