from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.exam import ExamCreate, ExamResponse, AddQuestionsToExam
from app.services import ExamService
from app.dependencies import get_current_teacher

router = APIRouter(prefix="/exams", tags=["Exams"])

@router.post("/", response_model=ExamResponse)
def create_exam(
    exam_data: ExamCreate, 
    db: Session = Depends(get_db), 
    teacher: User = Depends(get_current_teacher)
):
    return ExamService.create_exam(db, exam_data, teacher_id=teacher.user_id)

@router.post("/{exam_id}/questions", response_model=ExamResponse)
def add_questions_to_exam(
    exam_id: int, 
    data: AddQuestionsToExam, 
    db: Session = Depends(get_db),
    teacher: User = Depends(get_current_teacher)
):
    # Logic kiểm tra quyền sở hữu exam nên đặt ở đây
    updated_exam = ExamService.add_questions_to_exam(db, exam_id, data)
    if not updated_exam:
        raise HTTPException(status_code=404, detail="Không tìm thấy đề thi")
    return updated_exam