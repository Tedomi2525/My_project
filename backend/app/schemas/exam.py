from pydantic import (
    BaseModel,
    Field,
    computed_field,
    field_validator,
    ConfigDict
)
from typing import Optional, List
from datetime import datetime, timedelta, timezone


EXAM_STATUSES = {"draft", "published", "closed"}


# =====================================================
# Base Schema
# =====================================================
class ExamBase(BaseModel):
    title: str
    description: Optional[str] = None
    duration_minutes: int

    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    password: Optional[str] = None

    # ✅ Cho phép xem đáp án hay không
    allow_view_answers: bool = False
    # None = unlimited attempts, 1 = once, N > 1 = limited attempts
    max_attempts: Optional[int] = 1
    shuffle_questions: bool = False
    shuffle_options: bool = False
    status: str = "draft"

    @field_validator("start_time", "end_time")
    @classmethod
    def convert_to_vietnam_time(cls, v):
        if v is not None:
            if v.tzinfo is not None:
                vn_timezone = timezone(timedelta(hours=7))
                v = v.astimezone(vn_timezone)
            return v.replace(tzinfo=None)
        return v

    @field_validator("max_attempts")
    @classmethod
    def validate_max_attempts(cls, v):
        if v is not None and v < 1:
            raise ValueError("max_attempts must be >= 1 or null")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v not in EXAM_STATUSES:
            raise ValueError("status must be draft, published, or closed")
        return v


# =====================================================
# Create Schema
# =====================================================
class ExamCreate(ExamBase):

    class_ids: List[int] = Field(default_factory=list)
    questions: List[int] = Field(default_factory=list)


# =====================================================
# Update Schema
# =====================================================
class ExamUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = None

    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    password: Optional[str] = None

    # ✅ Có thể bật/tắt cho xem đáp án
    allow_view_answers: Optional[bool] = None
    max_attempts: Optional[int] = None
    shuffle_questions: Optional[bool] = None
    shuffle_options: Optional[bool] = None
    status: Optional[str] = None

    class_ids: Optional[List[int]] = None
    questions: Optional[List[int]] = None

    @field_validator("start_time", "end_time")
    @classmethod
    def convert_to_vietnam_time(cls, v):
        if v is not None:
            if v.tzinfo is not None:
                vn_timezone = timezone(timedelta(hours=7))
                v = v.astimezone(vn_timezone)
            return v.replace(tzinfo=None)
        return v

    @field_validator("max_attempts")
    @classmethod
    def validate_max_attempts(cls, v):
        if v is not None and v < 1:
            raise ValueError("max_attempts must be >= 1 or null")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v is not None and v not in EXAM_STATUSES:
            raise ValueError("status must be draft, published, or closed")
        return v


# =====================================================
# Response Schema
# =====================================================
class ExamResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    duration_minutes: int

    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    created_by: int

    password: Optional[str] = Field(default=None, exclude=True)

    allow_view_answers: bool
    max_attempts: Optional[int] = None
    shuffle_questions: bool
    shuffle_options: bool
    status: str = "draft"

    allowed_classes: List[int] = Field(default_factory=list)
    exam_questions: List[int] = Field(default_factory=list)

    @computed_field
    def has_password(self) -> bool:
        return bool(self.password)

    # ===== Extract class_id from ExamAllowedClass =====
    @field_validator("allowed_classes", mode="before")
    @classmethod
    def extract_class_ids(cls, v):
        if v and isinstance(v, list) and hasattr(v[0], "class_id"):
            return [item.class_id for item in v]
        return v or []

    # ===== Extract question_id from ExamQuestion =====
    @field_validator("exam_questions", mode="before")
    @classmethod
    def extract_question_ids(cls, v):
        if v and isinstance(v, list) and hasattr(v[0], "question_id"):
            return [item.question_id for item in v]
        return v or []

    model_config = ConfigDict(from_attributes=True)
