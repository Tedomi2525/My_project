from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.roles import normalize_role
from app.database import get_db
from app.dependencies import get_current_user, get_current_student
from app.schemas.exam_result import ExamResultResponse
from app.schemas.exam_result_detail import ExamResultDetailBase
from app.schemas.exam_result_teacher import ExamResultTeacherResponse
from app.schemas.result_review import ResultReviewResponse
from app.schemas.student_difficulty_stats import StudentDifficultyStatsResponse
from app.services.exam_result_service import ResultService

router = APIRouter(prefix="/results", tags=["Results"])


def get_role_name(user) -> str:
    return normalize_role(user.role)


@router.post("/submit/{exam_id}", response_model=ExamResultResponse)
def submit_exam(
    exam_id: int,
    answers: List[ExamResultDetailBase],
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if get_role_name(current_user) != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student permission required"
        )
    return ResultService.submit_exam(db, exam_id, current_user.id, answers)


@router.get("/{result_id}", response_model=ExamResultResponse)
def get_result(result_id: int, db: Session = Depends(get_db)):
    result = ResultService.get_result(db, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result


@router.get("/student/{student_id}", response_model=List[ExamResultResponse])
def get_student_history(student_id: int, db: Session = Depends(get_db)):
    return ResultService.get_student_history(db, student_id)


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
def update_score(result_id: int, score: float, db: Session = Depends(get_db)):
    result = ResultService.update_result_score(db, result_id, score)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return {"message": "Score updated", "new_score": result.total_score}


@router.delete("/{result_id}")
def delete_result(result_id: int, db: Session = Depends(get_db)):
    success = ResultService.delete_result(db, result_id)
    if not success:
        raise HTTPException(status_code=404, detail="Result not found")
    return {"message": "Result deleted"}
