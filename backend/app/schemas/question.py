from pydantic import BaseModel, Field, field_validator, model_validator
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

    @field_validator("question_type")
    @classmethod
    def normalize_question_type(cls, value):
        return (value or "MCQ").strip().upper()

    @field_validator("correct_answer")
    @classmethod
    def normalize_correct_answer(cls, value):
        answer_keys = [
            part.strip().upper()
            for part in value.split(",")
            if part.strip()
        ]
        return ",".join(dict.fromkeys(answer_keys))

    @model_validator(mode="after")
    def validate_answers(self):
        options = self.options or {}
        option_keys = set(options.keys())
        correct_keys = set(self.correct_answer.split(",")) if self.correct_answer else set()

        if len(option_keys) < 2:
            raise ValueError("Question must have at least 2 options")

        if any(str(value).strip() == "" for value in options.values()):
            raise ValueError("Options cannot be empty")

        if not correct_keys:
            raise ValueError("Question must have at least 1 correct answer")

        if not correct_keys.issubset(option_keys):
            raise ValueError("Correct answers must match option keys")

        if self.question_type == "MULTI_SELECT":
            if len(correct_keys) > len(option_keys):
                raise ValueError("Correct answer count cannot exceed option count")
        elif len(correct_keys) != 1:
            raise ValueError("MCQ questions must have exactly 1 correct answer")

        return self

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
