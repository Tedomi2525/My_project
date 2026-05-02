from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.core.roles import normalize_role
from app.database import get_db
from app.dependencies import get_current_student, get_current_user

from app.schemas.exam import ExamCreate, ExamResponse, ExamUpdate
from app.schemas.exam_session import (
    ExamAutosaveRequest,
    ExamSessionDetailResponse,
    ExamStartResponse,
    ExamViolationRequest,
    ExamViolationResponse,
)
from app.schemas.question import ExamQuestionResponse

from app.services.exam_service import ExamService


router = APIRouter(prefix="/exams", tags=["Exams"])


class PasswordCheckRequest(BaseModel):
    password: str


class StatusRequest(BaseModel):
    status: str


def get_role_name(user) -> str:
    return normalize_role(user.role)


def require_teacher(user):
    if get_role_name(user) != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher permission required"
        )
    return user


def require_exam_access(db: Session, exam_id: int, current_user):
    role = get_role_name(current_user)
    if role == "teacher":
        exam = ExamService.get_exam(db, exam_id)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        if str(exam.created_by) != str(current_user.id):
            raise HTTPException(status_code=403, detail="You do not have access to this exam")
        return

    if role != "student":
        raise HTTPException(status_code=403, detail="Permission denied")

    class_ids = getattr(current_user, "class_ids", None)
    if class_ids is None:
        current_user = get_current_student(current_user=current_user, db=db)
        class_ids = current_user.class_ids

    if not class_ids:
        raise HTTPException(status_code=400, detail="Student has no class")

    exams = ExamService.get_exams_for_student(db, class_ids)
    if not any(exam.id == exam_id for exam in exams):
        raise HTTPException(status_code=403, detail="You do not have access to this exam")


@router.get("/", response_model=List[ExamResponse])
def get_exams(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    require_teacher(current_user)
    exams = ExamService.get_exams(db)
    return [exam for exam in exams if str(exam.created_by) == str(current_user.id)]


@router.post("/", response_model=ExamResponse)
def create_exam(
    exam: ExamCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    require_teacher(current_user)
    return ExamService.create_exam(db, exam, current_user.id)


@router.get("/my-exams", response_model=List[ExamResponse])
def get_my_exams(
    db: Session = Depends(get_db),
    current_student=Depends(get_current_student)
):
    return ExamService.get_exams_for_student(db, current_student.class_ids)


@router.post("/{exam_id}/publish", response_model=ExamResponse)
def publish_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_teacher(current_user)
    require_exam_access(db, exam_id, current_user)
    exam = ExamService.set_status(db, exam_id, "published")
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam


@router.post("/{exam_id}/unpublish", response_model=ExamResponse)
def unpublish_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_teacher(current_user)
    require_exam_access(db, exam_id, current_user)
    exam = ExamService.set_status(db, exam_id, "draft")
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam


@router.post("/{exam_id}/close", response_model=ExamResponse)
def close_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_teacher(current_user)
    require_exam_access(db, exam_id, current_user)
    exam = ExamService.set_status(db, exam_id, "closed")
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam


@router.patch("/{exam_id}/status", response_model=ExamResponse)
def update_exam_status(
    exam_id: int,
    payload: StatusRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_teacher(current_user)
    require_exam_access(db, exam_id, current_user)
    exam = ExamService.set_status(db, exam_id, payload.status)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam


@router.post("/{exam_id}/start", response_model=ExamStartResponse)
def start_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_student=Depends(get_current_student),
):
    require_exam_access(db, exam_id, current_student)
    return ExamService.start_exam_session(db, exam_id, current_student.id)


@router.put("/{exam_id}/autosave", response_model=ExamStartResponse)
def autosave_exam(
    exam_id: int,
    payload: ExamAutosaveRequest,
    db: Session = Depends(get_db),
    current_student=Depends(get_current_student),
):
    require_exam_access(db, exam_id, current_student)
    return ExamService.autosave_exam_session(
        db,
        exam_id,
        current_student.id,
        payload.answers,
    )


@router.post("/{exam_id}/violations", response_model=ExamViolationResponse)
def log_exam_violation(
    exam_id: int,
    payload: ExamViolationRequest,
    db: Session = Depends(get_db),
    current_student=Depends(get_current_student),
):
    require_exam_access(db, exam_id, current_student)
    return ExamService.log_violation(
        db,
        exam_id,
        current_student.id,
        payload.reason,
    )


@router.get("/{exam_id}/sessions", response_model=List[ExamSessionDetailResponse])
def get_exam_sessions(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_teacher(current_user)
    sessions = ExamService.get_exam_sessions_for_teacher(db, exam_id, current_user.id)
    if sessions is None:
        raise HTTPException(status_code=404, detail="Exam not found or not owned by current teacher")
    return sessions


@router.get("/{exam_id}", response_model=ExamResponse)
def get_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    require_exam_access(db, exam_id, current_user)

    exam = ExamService.get_exam(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    return exam


@router.put("/{exam_id}", response_model=ExamResponse)
def update_exam(
    exam_id: int,
    exam_in: ExamUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    require_teacher(current_user)
    require_exam_access(db, exam_id, current_user)

    exam_data = exam_in.model_dump(exclude_unset=True)
    exam = ExamService.update_exam(db, exam_id, exam_data)

    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    return exam


@router.delete("/{exam_id}")
def delete_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    require_teacher(current_user)
    require_exam_access(db, exam_id, current_user)

    success = ExamService.delete_exam(db, exam_id)
    if not success:
        raise HTTPException(status_code=404, detail="Exam not found")

    return {"message": "Exam deleted successfully"}


@router.get("/{exam_id}/questions", response_model=List[ExamQuestionResponse])
def get_exam_questions(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    require_exam_access(db, exam_id, current_user)

    exam = ExamService.get_exam(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    return ExamService.get_exam_questions(db, exam_id)


@router.post("/{exam_id}/check-password")
def check_exam_password(
    exam_id: int,
    payload: PasswordCheckRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    require_exam_access(db, exam_id, current_user)
    is_ok = ExamService.check_exam_password(db, exam_id, payload.password)
    if not is_ok:
        raise HTTPException(status_code=400, detail="Wrong exam password")
    return {"success": True}
