from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Union

from pydantic import BaseModel
from app.core.roles import normalize_role
from app.database import get_db
from app.dependencies import get_current_user, get_current_student
from app.schemas.exam_result import ExamResultResponse
from app.schemas.exam_result_detail import ExamResultDetailBase
from app.schemas.exam_result_teacher import ExamResultTeacherResponse
from app.schemas.result_review import ResultReviewResponse
from app.schemas.student_difficulty_stats import StudentDifficultyStatsResponse
from app.schemas.question_analytics import QuestionAnalyticsResponse
from app.services.exam_result_service import ResultService

router = APIRouter(prefix="/results", tags=["Results"])


class SubmitExamRequest(BaseModel):
    answers: List[ExamResultDetailBase]
    password: str | None = None


def get_role_name(user) -> str:
    return normalize_role(user.role)


def ensure_result_access(db: Session, result_id: int, current_user):
    result = ResultService.get_result(db, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    role = get_role_name(current_user)
    if role == "admin":
        return result

    if role == "student":
        if result.student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own result"
            )
        return result

    if role == "teacher":
        if not result.exam or result.exam.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access results from your own exams"
            )
        return result

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Permission denied"
    )


@router.post("/submit/{exam_id}", response_model=ExamResultResponse)
def submit_exam(
    exam_id: int,
    payload: Union[List[ExamResultDetailBase], SubmitExamRequest],
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if get_role_name(current_user) != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student permission required"
        )

    if isinstance(payload, list):
        answers = payload
        password = None
    else:
        answers = payload.answers
        password = payload.password

    return ResultService.submit_exam(db, exam_id, current_user.id, answers, password)


@router.get("/{result_id}", response_model=ExamResultResponse)
def get_result(
    result_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return ensure_result_access(db, result_id, current_user)


@router.get("/student/{student_id}", response_model=List[ExamResultResponse])
def get_student_history(
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    role = get_role_name(current_user)

    if role == "student" and current_user.id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own history"
        )
    if role not in {"student", "teacher", "admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    results = ResultService.get_student_history(db, student_id)
    if role == "teacher":
        results = [
            result for result in results
            if result.exam and result.exam.created_by == current_user.id
        ]
    return results


@router.get("/student/{student_id}/difficulty-stats", response_model=StudentDifficultyStatsResponse)
def get_student_difficulty_stats(
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_student)
):
    if current_user.id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own stats"
        )

    return ResultService.get_student_difficulty_stats(db, student_id)


@router.get("/exam/{exam_id}", response_model=List[ExamResultTeacherResponse])
def get_exam_results_for_teacher(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if get_role_name(current_user) != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher permission required"
        )

    results = ResultService.get_exam_results_for_teacher(db, exam_id, current_user.id)
    if results is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found or not owned by current teacher"
        )
    return results


@router.get("/exam/{exam_id}/question-analytics", response_model=List[QuestionAnalyticsResponse])
def get_question_analytics_for_teacher(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if get_role_name(current_user) != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher permission required"
        )

    analytics = ResultService.get_question_analytics_for_teacher(db, exam_id, current_user.id)
    if analytics is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found or not owned by current teacher"
        )
    return analytics


@router.get("/{result_id}/review", response_model=ResultReviewResponse)
def get_result_review(
    result_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    review = ResultService.get_result_review(db, result_id)
    if not review:
        raise HTTPException(status_code=404, detail="Result not found")

    role = get_role_name(current_user)

    if role == "student":
        if review["student_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only review your own result"
            )
        if not review["allow_view_answers"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Teacher has not enabled answer review for this exam"
            )
    elif role == "teacher":
        exam = ResultService.get_result(db, result_id)
        if not exam or not exam.exam or exam.exam.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only review results from your own exams"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    return review


@router.put("/{result_id}/score")
def update_score(
    result_id: int,
    score: float,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    result_for_access = ensure_result_access(db, result_id, current_user)
    role = get_role_name(current_user)
    if role not in {"teacher", "admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher permission required"
        )
    if role == "teacher" and (
        not result_for_access.exam or result_for_access.exam.created_by != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update scores from your own exams"
        )

    result = ResultService.update_result_score(db, result_id, score)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return {"message": "Score updated", "new_score": result.total_score}


@router.delete("/{result_id}")
def delete_result(
    result_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    result_for_access = ensure_result_access(db, result_id, current_user)
    role = get_role_name(current_user)
    if role not in {"teacher", "admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher permission required"
        )
    if role == "teacher" and (
        not result_for_access.exam or result_for_access.exam.created_by != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete results from your own exams"
        )

    success = ResultService.delete_result(db, result_id)
    if not success:
        raise HTTPException(status_code=404, detail="Result not found")
    return {"message": "Result deleted"}
