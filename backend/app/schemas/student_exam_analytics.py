from typing import List
from pydantic import BaseModel, Field


class StudentAnalyticsBucket(BaseModel):
    key: str
    label: str
    correct: int
    total: int
    correct_rate: float


class StudentExamAnalyticsResponse(BaseModel):
    result_id: int
    exam_id: int
    exam_title: str
    student_id: int
    student_name: str
    student_code: str = ""
    total_score: float
    correct_answers: int
    total_questions: int
    correct_rate: float
    by_topic: List[StudentAnalyticsBucket] = Field(default_factory=list)
    by_difficulty: List[StudentAnalyticsBucket] = Field(default_factory=list)
