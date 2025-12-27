from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# --- SỬA LỖI Ở DÒNG NÀY: Thêm AnswerCreate vào import ---
from app.schemas.answer import AnswerResponse, AnswerCreate 

# Input: Khi bắt đầu làm bài
class AttemptCreate(BaseModel):
    exam_id: int

# Input: Khi nộp bài (Gửi toàn bộ đáp án 1 lần - Cách nộp Bulk)
class SubmitExamRequest(BaseModel):
    # Bây giờ AnswerCreate đã được định nghĩa nhờ dòng import trên
    answers: List[AnswerCreate]

# Response: Kết quả bài thi
class ExamAttemptResponse(BaseModel):
    attempt_id: int
    exam_id: int
    student_id: int
    score: float
    started_at: datetime
    submitted_at: Optional[datetime] = None
    
    # Danh sách chi tiết các câu đã trả lời (để xem lại bài)
    answers: List[AnswerResponse] = []

    class Config:
        from_attributes = True