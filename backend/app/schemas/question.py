from pydantic import BaseModel, Field, model_validator
from typing import Optional, Dict, Any, List
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


class ExamQuestionResponse(BaseModel):
    id: int
    content: str
    question_type: Optional[str] = "MCQ"
    difficulty: DifficultyLevel = DifficultyLevel.EASY
    options: Optional[Dict[str, Any]] = None
    created_by: int

    class Config:
        from_attributes = True


class QuestionImportRequest(BaseModel):
    filename: str = Field(min_length=1)
    csv_content: str = Field(min_length=1)


class QuestionImportError(BaseModel):
    row: int
    message: str


class QuestionImportResponse(BaseModel):
    imported_count: int
    total_rows: int
    errors: List[QuestionImportError] = Field(default_factory=list)


class RandomQuestionSelectionRequest(BaseModel):
    easy_count: int = Field(default=0, ge=0)
    medium_count: int = Field(default=0, ge=0)
    hard_count: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_total(self):
        if self.easy_count + self.medium_count + self.hard_count <= 0:
            raise ValueError("At least one difficulty count must be greater than 0")
        return self


class RandomQuestionSelectionResponse(BaseModel):
    question_ids: List[int]
    easy_count: int
    medium_count: int
    hard_count: int
    total_selected: int
