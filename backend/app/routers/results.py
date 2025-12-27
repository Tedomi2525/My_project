from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.result import AttemptCreate, SubmitExamRequest, ExamAttemptResponse
from app.services import ResultService
from app.dependencies import get_current_user

router = APIRouter(prefix="/attempts", tags=["Exam Taking"])

@router.post("/start", response_model=ExamAttemptResponse)
def start_exam(
    data: AttemptCreate, 
    db: Session = Depends(get_db), 
    student: User = Depends(get_current_user)
):
    """Bắt đầu làm bài -> Tạo bản ghi Attempt"""
    return ResultService.start_exam(db, data.exam_id, student.user_id)

@router.post("/{attempt_id}/submit", response_model=ExamAttemptResponse)
def submit_exam(
    attempt_id: int, 
    submission: SubmitExamRequest, 
    db: Session = Depends(get_db),
    student: User = Depends(get_current_user)
):
    """Nộp bài -> Hệ thống chấm điểm ngay lập tức"""
    result = ResultService.submit_exam(db, attempt_id, submission)
    if not result:
        raise HTTPException(status_code=404, detail="Lượt thi không tồn tại")
    return result
from typing import List
from app.dependencies import get_current_teacher

@router.get("/exam/{exam_id}", response_model=List[ExamAttemptResponse])
def get_exam_results(
    exam_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(get_current_teacher)
):
    # (Có thể thêm bước kiểm tra xem giáo viên này có tạo ra exam_id này không)
    return ResultService.get_results_by_exam(db, exam_id)