from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.user import UserResponse

class ClassroomBase(BaseModel):
    class_name: str

class ClassroomCreate(ClassroomBase):
    pass # Giống Base, teacher_id sẽ lấy từ token của người đang login

class ClassroomUpdate(BaseModel):
    class_name: Optional[str] = None

class ClassroomResponse(ClassroomBase):
    class_id: int
    teacher_id: int
    created_at: datetime
    # Có thể trả về thông tin giáo viên nếu cần
    # teacher: Optional[UserResponse] = None 

    class Config:
        from_attributes = True