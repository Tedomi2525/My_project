from pydantic import BaseModel


class QuestionAnalyticsResponse(BaseModel):
    question_id: int
    content: str
    difficulty: str | None = None
    total_answers: int
    correct_answers: int
    wrong_answers: int
    correct_rate: float
    wrong_rate: float
