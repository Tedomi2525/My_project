from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.schemas.question import QuestionCreate, QuestionResponse
from app.services import QuestionService
from app.dependencies import get_current_teacher

router = APIRouter(prefix="/questions", tags=["Questions"])

@router.post("/", response_model=QuestionResponse)
def create_question(
    question: QuestionCreate, 
    db: Session = Depends(get_db), 
    teacher: User = Depends(get_current_teacher)
):
    return QuestionService.create_question(db, question, teacher_id=teacher.user_id)

@router.get("/", response_model=List[QuestionResponse])
def get_my_questions(
    db: Session = Depends(get_db), 
    teacher: User = Depends(get_current_teacher)
):
    return QuestionService.get_questions_by_teacher(db, teacher.user_id)