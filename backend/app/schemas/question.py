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
    difficulty: DifficultyLevel = DifficultyLevel.EASY
    options: Optional[Dict[str, Any]] = None
    correct_answer: str = ""
    image_url: Optional[str] = None
    code_snippet: Optional[str] = None
    code_language: Optional[str] = None
    explanation: Optional[str] = None
    topic_id: Optional[int] = None
    visibility: str = "public"

    @field_validator("question_type")
    @classmethod
    def normalize_question_type(cls, value):
        value = (value or "MCQ").strip().upper()
        if value not in {"MCQ", "MULTI_SELECT", "TRUE_FALSE", "FILL_BLANK", "ESSAY"}:
            raise ValueError("Unsupported question type")
        return value

    @field_validator("correct_answer")
    @classmethod
    def normalize_correct_answer(cls, value):
        return (value or "").strip()

    @field_validator("visibility")
    @classmethod
    def normalize_visibility(cls, value):
        normalized = (value or "public").strip().lower()
        if normalized not in {"public", "private"}:
            raise ValueError("visibility must be public or private")
        return normalized

    @model_validator(mode="after")
    def validate_answers(self):
        if self.question_type == "ESSAY":
            self.options = None
            return self
        if self.question_type == "FILL_BLANK":
            self.options = None
            if not self.correct_answer:
                raise ValueError("Fill blank requires an answer")
            return self
        if self.question_type == "TRUE_FALSE":
            self.options = {"TRUE": "Đúng", "FALSE": "Sai"}
            self.correct_answer = self.correct_answer.upper()
            if self.correct_answer not in {"TRUE", "FALSE"}:
                raise ValueError("True/false answer must be TRUE or FALSE")
            return self
        options = self.options or {}
        option_keys = {str(key).upper() for key in options.keys()}
        answers = list(dict.fromkeys(part.strip().upper() for part in self.correct_answer.split(",") if part.strip()))
        self.correct_answer = ",".join(answers)
        if len(options) < 2 or any(str(value).strip() == "" for value in options.values()):
            raise ValueError("Question requires at least 2 non-empty options")
        if not answers or not set(answers).issubset(option_keys):
            raise ValueError("Correct answers must match option keys")
        if self.question_type == "MCQ" and len(answers) != 1:
            raise ValueError("MCQ requires exactly one correct answer")
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
    topic_id: Optional[int] = None
    visibility: str = "public"
    image_url: Optional[str] = None
    code_snippet: Optional[str] = None
    code_language: Optional[str] = None
    explanation: Optional[str] = None
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


class QuestionSuggestionRequest(BaseModel):
    target_difficulty: DifficultyLevel = DifficultyLevel.EASY
    topic_id: Optional[int] = None
    count: int = Field(default=3, ge=1, le=10)


class QuestionSuggestionItem(BaseModel):
    content: str
    question_type: str = "MCQ"
    difficulty: DifficultyLevel
    options: Dict[str, Any]
    correct_answer: str
    topic_id: Optional[int] = None
    source_question_id: int
    source_content: str
    reason: str


class QuestionSuggestionResponse(BaseModel):
    suggestions: List[QuestionSuggestionItem] = Field(default_factory=list)
    total_generated: int


class QuestionTopicBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None


class QuestionTopicCreate(QuestionTopicBase):
    pass


class QuestionTopicResponse(QuestionTopicBase):
    id: int
    created_by: Optional[int] = None

    class Config:
        from_attributes = True
