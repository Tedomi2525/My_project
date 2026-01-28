from pydantic import BaseModel, Field, computed_field, field_validator
from typing import Optional, List
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
    created_by: int
    class_ids: List[int] = []  # 👈 [THÊM] Nhận danh sách ID lớp từ Frontend

# --- Update Schema ---
class ExamUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    password: Optional[str] = None
    class_ids: Optional[List[int]] = None # 👈 [THÊM] Cho phép update danh sách lớp

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
    
    # 👈 [THÊM] Trả về danh sách ID lớp để Frontend hiển thị khi Edit
    allowed_classes: List[int] = Field(default_factory=list) 

    @computed_field
    def has_password(self) -> bool:
        return bool(self.password)

    # 👈 [THÊM] Validator để lấy ID từ relationship SQLAlchemy (ExamAllowedClass)
    @field_validator('allowed_classes', mode='before')
    def extract_class_ids(cls, v):
        # Nếu v là danh sách các object ExamAllowedClass từ DB
        if v and isinstance(v, list) and hasattr(v[0], 'class_id'):
            return [item.class_id for item in v]
        return v or []

    class Config:
        from_attributes = True