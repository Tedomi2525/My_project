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