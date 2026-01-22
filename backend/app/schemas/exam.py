from pydantic import BaseModel, Field, computed_field, field_validator
from typing import Optional
from datetime import datetime, timedelta, timezone

# --- Base Schema ---
class ExamBase(BaseModel):
    title: str
    description: Optional[str] = None
    duration_minutes: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    password: Optional[str] = None 

    @field_validator('start_time', 'end_time')
    @classmethod
    def convert_to_vietnam_time(cls, v):
        if v is not None:
            if v.tzinfo is not None:
                vn_timezone = timezone(timedelta(hours=7))
                v = v.astimezone(vn_timezone)
            return v.replace(tzinfo=None)
        return v

# --- Create Schema ---
class ExamCreate(ExamBase):
    created_by: int  # Hiện tại client sẽ gửi field này lên (sau này có Auth thì bỏ sau)

# --- Update Schema (Dùng cho router update) ---
class ExamUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    password: Optional[str] = None

    @field_validator('start_time', 'end_time')
    @classmethod
    def convert_to_vietnam_time(cls, v):
        if v is not None:
            if v.tzinfo is not None:
                vn_timezone = timezone(timedelta(hours=7))
                v = v.astimezone(vn_timezone)
            return v.replace(tzinfo=None)
        return v

# --- Response Schema ---
class ExamResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    duration_minutes: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_by: int
    password: Optional[str] = Field(default=None, exclude=True)

    @computed_field
    def has_password(self) -> bool:
        return bool(self.password)

    class Config:
        from_attributes = True