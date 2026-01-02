from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class ExamStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ENDED = "ended"

class ExamBase(BaseModel):
    title: str
    # Map các trường camelCase từ Vue sang snake_case
    duration_minutes: int = Field(..., alias="duration")
    start_time: Optional[datetime] = Field(None, alias="startTime")
    end_time: Optional[datetime] = Field(None, alias="endTime")
    status: ExamStatus = ExamStatus.DRAFT
    show_answers: bool = Field(True, alias="showAnswers")
    password: Optional[str] = None

class ExamCreate(ExamBase):
    # Danh sách ID câu hỏi và ID sinh viên gửi lên khi tạo đề
    questions: List[int] = []
    allowed_students: List[int] = Field([], alias="allowedStudents")

class ExamResponse(ExamBase):
    exam_id: int
    created_at: datetime
    # Hai mảng này cần query thêm để điền vào
    questions: List[int] = [] 
    allowed_students: List[int] = Field([], alias="allowedStudents")

    class Config:
        from_attributes = True
        populate_by_name = True # Bắt buộc có để trả về camelCase cho Vue