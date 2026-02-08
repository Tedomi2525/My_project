from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User

from app.schemas.exam import ExamCreate, ExamResponse, ExamUpdate
from app.schemas.exam_question import ExamQuestionCreate, ExamQuestionResponse
from app.schemas.question import QuestionResponse

from app.services.exam_service import ExamService


router = APIRouter(prefix="/exams", tags=["Exams"])


# ---------- ROLE CHECK (GIỐNG CLASS) ----------
def require_teacher(user: User):
    role = user.role
    if hasattr(role, "value"):
        role = role.value

    if str(role).lower() != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher permission required"
        )
    return user


# ==========================================
#               EXAM CRUD
# ==========================================

@router.get("/", response_model=List[ExamResponse])
def get_exams(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_teacher(current_user)
    return ExamService.get_exams(db)


@router.post("/", response_model=ExamResponse)
def create_exam(
    exam: ExamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_teacher(current_user)
    return ExamService.create_exam(db, exam, current_user)


@router.get("/{exam_id}", response_model=ExamResponse)
def get_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_teacher(current_user)

    exam = ExamService.get_exam(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    return exam


@router.put("/{exam_id}", response_model=ExamResponse)
def update_exam(
    exam_id: int,
    exam_in: ExamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_teacher(current_user)

    exam_data = exam_in.model_dump(exclude_unset=True)
    exam = ExamService.update_exam(db, exam_id, exam_data)

    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    return exam


@router.delete("/{exam_id}")
def delete_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_teacher(current_user)

    success = ExamService.delete_exam(db, exam_id)
    if not success:
        raise HTTPException(status_code=404, detail="Exam not found")

    return {"message": "Exam deleted successfully"}


# ==========================================
#        QUẢN LÝ CÂU HỎI TRONG ĐỀ
# ==========================================

@router.get("/{exam_id}/questions", response_model=List[QuestionResponse])
def get_exam_questions(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_teacher(current_user)

    exam = ExamService.get_exam(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    return ExamService.get_exam_questions(db, exam_id)


@router.post("/{exam_id}/questions", response_model=ExamQuestionResponse)
def add_question_to_exam(
    exam_id: int,
    question_link: ExamQuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_teacher(current_user)

    if question_link.exam_id != exam_id:
        raise HTTPException(
            status_code=400,
            detail="Exam ID mismatch in payload"
        )

    return ExamService.add_question_to_exam(
        db, exam_id, question_link.question_id
    )


@router.delete("/{exam_id}/questions/{question_id}")
def remove_question_from_exam(
    exam_id: int,
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_teacher(current_user)

    success = ExamService.remove_question_from_exam(
        db, exam_id, question_id
    )
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Question not found in this exam"
        )

    return {"message": "Question removed from exam"}
