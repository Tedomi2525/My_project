from pydantic import BaseModel
from typing import List
from datetime import datetime
from .answer import AnswerSubmit

# Nhận một object chứa ID đề thi và danh sách câu trả lời
class ExamSubmission(BaseModel):
    exam_id: int
    answers: List[AnswerSubmit]

# Trả về kết quả sau khi chấm
class SubmissionResult(BaseModel):
    score: float
    correct_count: int
    total_questions: int
    submitted_at: datetime