from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.models.exam import ExamStatus
from app.schemas.question import QuestionResponse

# --- Phần xử lý câu hỏi trong đề thi ---
class ExamQuestionLinkBase(BaseModel):
    question_id: int
    point_value: float = 1.0

class ExamQuestionResponse(ExamQuestionLinkBase):
    # Khi trả về, cần hiện chi tiết nội dung câu hỏi để hiển thị lên đề
    question: QuestionResponse 
    
    class Config:
        from_attributes = True

# --- Phần xử lý Đề thi ---
class ExamBase(BaseModel):
    title: str
    duration_minutes: int
    status: ExamStatus = ExamStatus.DRAFT

class ExamCreate(ExamBase):
    pass

# Dùng để thêm list câu hỏi vào đề
class AddQuestionsToExam(BaseModel):
    questions: List[ExamQuestionLinkBase]

class ExamResponse(ExamBase):
    exam_id: int
    teacher_id: int
    created_at: datetime
    # Danh sách câu hỏi trong đề (kèm điểm)
    questions: List[ExamQuestionResponse] = []

    class Config:
        from_attributes = True