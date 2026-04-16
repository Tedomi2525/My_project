from typing import List
from pydantic import BaseModel, Field


class DifficultyStat(BaseModel):
    difficulty: str
    attempted: int
    wrong: int
    wrong_rate: float


class StudentDifficultyStatsResponse(BaseModel):
    student_id: int
    total_attempted: int
    total_wrong: int
    by_difficulty: List[DifficultyStat] = Field(default_factory=list)
