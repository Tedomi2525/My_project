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
# app/routers/exams.py (Thêm vào cuối file)
from app.models.exam import ExamStatus

# Xóa đề thi
@router.delete("/{exam_id}", status_code=204)
def delete_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(get_current_teacher)
):
    success = ExamService.delete_exam(db, exam_id, teacher.user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Không tìm thấy đề thi hoặc bạn không có quyền xóa")
    return None

# Sửa trạng thái đề thi (Ví dụ: Kích hoạt đề hoặc Kết thúc đề)
@router.patch("/{exam_id}/status", response_model=ExamResponse)
def change_exam_status(
    exam_id: int,
    status: ExamStatus, # Enum: Draft, Active, Finished
    db: Session = Depends(get_db),
    teacher: User = Depends(get_current_teacher)
):
    updated_exam = ExamService.update_exam_status(db, exam_id, status, teacher.user_id)
    if not updated_exam:
        raise HTTPException(status_code=404, detail="Lỗi cập nhật trạng thái")
    return updated_exam