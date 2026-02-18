from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ResultReviewQuestion(BaseModel):
    question_id: int
    content: str
    options: Optional[Dict[str, Any]] = None
    correct_answer: str
    student_answer: str = ""
    is_correct: bool = False


class ResultReviewResponse(BaseModel):
    result_id: int
    exam_id: int
    exam_title: str
    student_id: int
    total_score: float
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    allow_view_answers: bool
    questions: List[ResultReviewQuestion] = Field(default_factory=list)
