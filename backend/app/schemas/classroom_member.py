from pydantic import BaseModel
from datetime import datetime
from typing import List

# Input: Giáo viên gửi lên danh sách ID sinh viên muốn thêm
class AddStudentToClass(BaseModel):
    student_ids: List[int]

# Response: Trả về thông tin ghi danh
class EnrollmentResponse(BaseModel):
    class_id: int
    student_id: int
    joined_at: datetime

    class Config:
        from_attributes = True