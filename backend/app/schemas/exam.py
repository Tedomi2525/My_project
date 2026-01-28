from pydantic import (
    BaseModel,
    Field,
    computed_field,
    field_validator,
    ConfigDict
)
from typing import Optional, List
from datetime import datetime, timedelta, timezone


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

    @field_validator("start_time", "end_time")
    @classmethod
    def convert_to_vietnam_time(cls, v):
        if v is not None:
            if v.tzinfo is not None:
                vn_timezone = timezone(timedelta(hours=7))
                v = v.astimezone(vn_timezone)
            return v.replace(tzinfo=None)
        return v


# =====================================================
# Create Schema
# =====================================================
class ExamCreate(ExamBase):
    created_by: int
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

    # ✅ Trả trạng thái cho FE
    allow_view_answers: bool

    allowed_classes: List[int] = Field(default_factory=list)
    questions: List[int] = Field(default_factory=list)

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
    @field_validator("questions", mode="before")
    @classmethod
    def extract_question_ids(cls, v):
        if v and isinstance(v, list) and hasattr(v[0], "question_id"):
            return [item.question_id for item in v]
        return v or []

    model_config = ConfigDict(from_attributes=True)
