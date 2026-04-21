from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.dependencies import get_current_teacher
from app.schemas.question import (
    QuestionCreate,
    QuestionImportRequest,
    QuestionImportResponse,
    QuestionResponse,
    RandomQuestionSelectionRequest,
    RandomQuestionSelectionResponse,
)
from app.services.question_service import QuestionService

router = APIRouter(prefix="/questions", tags=["Questions"])

@router.post("/", response_model=QuestionResponse)
def create_question(
    question: QuestionCreate,
    db: Session = Depends(get_db),
    current_teacher=Depends(get_current_teacher)
):
    question_data = question.model_copy(update={"created_by": current_teacher.id})
    return QuestionService.create_question(db, question_data)

@router.get("/", response_model=List[QuestionResponse])
def get_questions(
    db: Session = Depends(get_db),
    current_teacher=Depends(get_current_teacher)
):
    return QuestionService.get_questions_for_teacher(db, current_teacher.id)

@router.post("/import/csv", response_model=QuestionImportResponse)
def import_questions_from_csv(
    payload: QuestionImportRequest,
    db: Session = Depends(get_db),
    current_teacher=Depends(get_current_teacher)
):
    try:
        return QuestionService.import_questions_from_csv(
            db=db,
            teacher_id=current_teacher.id,
            csv_content=payload.csv_content,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.post("/random-selection", response_model=RandomQuestionSelectionResponse)
def get_random_question_selection(
    payload: RandomQuestionSelectionRequest,
    db: Session = Depends(get_db),
    current_teacher=Depends(get_current_teacher)
):
    try:
        question_ids = QuestionService.get_random_questions_by_difficulty(
            db=db,
            teacher_id=current_teacher.id,
            easy_count=payload.easy_count,
            medium_count=payload.medium_count,
            hard_count=payload.hard_count,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "question_ids": question_ids,
        "easy_count": payload.easy_count,
        "medium_count": payload.medium_count,
        "hard_count": payload.hard_count,
        "total_selected": len(question_ids),
    }

@router.get("/{question_id}", response_model=QuestionResponse)
def get_question(question_id: int, db: Session = Depends(get_db)):
    q = QuestionService.get_question(db, question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    return q

@router.put("/{question_id}", response_model=QuestionResponse)
def update_question(
    question_id: int,
    data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_teacher=Depends(get_current_teacher)
):
    existing_question = QuestionService.get_question(db, question_id)
    if not existing_question:
        raise HTTPException(status_code=404, detail="Question not found")

    accessible_ids = {
        question.id
        for question in QuestionService.get_questions_for_teacher(db, current_teacher.id)
    }
    if question_id not in accessible_ids:
        raise HTTPException(status_code=403, detail="You do not have access to this question")

    data.pop("created_by", None)
    q = QuestionService.update_question(db, question_id, data)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    return q

@router.delete("/{question_id}")
def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_teacher=Depends(get_current_teacher)
):
    accessible_ids = {
        question.id
        for question in QuestionService.get_questions_for_teacher(db, current_teacher.id)
    }
    if question_id not in accessible_ids:
        raise HTTPException(status_code=403, detail="You do not have access to this question")

    success = QuestionService.delete_question(db, question_id)
    if not success:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"message": "Question deleted"}
