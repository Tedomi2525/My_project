from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.schemas.question import QuestionCreate, QuestionResponse
from app.services.question_service import QuestionService

router = APIRouter(prefix="/questions", tags=["Questions"])

@router.post("/", response_model=QuestionResponse)
def create_question(question: QuestionCreate, db: Session = Depends(get_db)):
    return QuestionService.create_question(db, question)

@router.get("/", response_model=List[QuestionResponse])
def get_questions(db: Session = Depends(get_db)):
    return QuestionService.get_questions(db)

@router.get("/{question_id}", response_model=QuestionResponse)
def get_question(question_id: int, db: Session = Depends(get_db)):
    q = QuestionService.get_question(db, question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    return q

@router.put("/{question_id}", response_model=QuestionResponse)
def update_question(question_id: int, data: Dict[str, Any], db: Session = Depends(get_db)):
    q = QuestionService.update_question(db, question_id, data)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    return q

@router.delete("/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    success = QuestionService.delete_question(db, question_id)
    if not success:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"message": "Question deleted"}