from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.dependencies import get_current_student, get_current_user
from app.models.class_student import ClassStudent
from app.models.user import User

from app.schemas.exam import ExamCreate, ExamResponse, ExamUpdate
from app.schemas.exam_question import ExamQuestionCreate, ExamQuestionResponse
from app.schemas.question import QuestionResponse

from app.services.exam_service import ExamService


router = APIRouter(prefix="/exams", tags=["Exams"])


def get_role_name(user: User) -> str:
    role = user.role
    if hasattr(role, "value"):
        role = role.value
    return str(role).lower()


# ---------- ROLE CHECK (GIONG CLASS) ----------
def require_teacher(user: User):
    if get_role_name(user) != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher permission required"
        )
    return user


def require_exam_access(db: Session, exam_id: int, current_user: User):
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

    class_student = (
        db.query(ClassStudent)
        .filter(ClassStudent.student_id == current_user.id)
        .first()
    )
    if not class_student:
        raise HTTPException(status_code=400, detail="Student has no class")

    exams = ExamService.get_exams_for_student(db, class_student.class_id)
    if not any(exam.id == exam_id for exam in exams):
        raise HTTPException(status_code=403, detail="You do not have access to this exam")


# ==========================================
#               EXAM CRUD
# ==========================================

@router.get("/", response_model=List[ExamResponse])
def get_exams(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_teacher(current_user)
    exams = ExamService.get_exams(db)
    return [exam for exam in exams if str(exam.created_by) == str(current_user.id)]


@router.post("/", response_model=ExamResponse)
def create_exam(
    exam: ExamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_teacher(current_user)
    return ExamService.create_exam(db, exam, current_user.id)


@router.get("/my-exams", response_model=List[ExamResponse])
def get_my_exams(
    db: Session = Depends(get_db),
    current_student: User = Depends(get_current_student)
):
    class_id = current_student.class_id
    return ExamService.get_exams_for_student(db, class_id)


@router.get("/{exam_id}", response_model=ExamResponse)
def get_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
    current_user: User = Depends(get_current_user)
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
    current_user: User = Depends(get_current_user)
):
    require_teacher(current_user)
    require_exam_access(db, exam_id, current_user)

    success = ExamService.delete_exam(db, exam_id)
    if not success:
        raise HTTPException(status_code=404, detail="Exam not found")

    return {"message": "Exam deleted successfully"}


@router.get("/{exam_id}/questions", response_model=List[QuestionResponse])
def get_exam_questions(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_exam_access(db, exam_id, current_user)

    exam = ExamService.get_exam(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    return ExamService.get_exam_questions(db, exam_id)
