from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
# 👇 Import thêm ExamUpdate
from app.schemas.exam import ExamCreate, ExamResponse, ExamUpdate
from app.schemas.exam_question import ExamQuestionCreate, ExamQuestionResponse
from app.services.exam_service import ExamService

router = APIRouter(prefix="/exams", tags=["Exams"])

# --- EXAM CRUD ---

@router.post("/", response_model=ExamResponse)
def create_exam(exam: ExamCreate, db: Session = Depends(get_db)):
    # Validator trong ExamCreate sẽ chạy ở đây -> data sạch -> OK
    return ExamService.create_exam(db, exam)

@router.get("/", response_model=List[ExamResponse])
def get_exams(db: Session = Depends(get_db)):
    return ExamService.get_exams(db)

@router.get("/{exam_id}", response_model=ExamResponse)
def get_exam(exam_id: int, db: Session = Depends(get_db)):
    exam = ExamService.get_exam(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam

# 👇 SỬA HÀM NAY: Đổi exam_data: dict thành exam_in: ExamUpdate
@router.put("/{exam_id}", response_model=ExamResponse)
def update_exam(
    exam_id: int, 
    exam_in: ExamUpdate, # Dùng Schema để kích hoạt Validator xóa Timezone
    db: Session = Depends(get_db)
):
    # Chuyển Schema thành dict, loại bỏ các trường user không gửi (exclude_unset)
    exam_data = exam_in.model_dump(exclude_unset=True)
    
    exam = ExamService.update_exam(db, exam_id, exam_data)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam

@router.delete("/{exam_id}")
def delete_exam(exam_id: int, db: Session = Depends(get_db)):
    success = ExamService.delete_exam(db, exam_id)
    if not success:
         raise HTTPException(status_code=404, detail="Exam not found")
    return {"message": "Exam deleted"}

# --- QUẢN LÝ CÂU HỎI TRONG ĐỀ ---
# (Giữ nguyên phần add/remove question như cũ)
@router.post("/{exam_id}/questions", response_model=ExamQuestionResponse)
def add_question_to_exam(
    exam_id: int, 
    question_link: ExamQuestionCreate, 
    db: Session = Depends(get_db)
):
    if question_link.exam_id != exam_id:
        raise HTTPException(status_code=400, detail="Exam ID mismatch")
    return ExamService.add_question_to_exam(db, question_link)

@router.delete("/{exam_id}/questions/{question_id}")
def remove_question_from_exam(exam_id: int, question_id: int, db: Session = Depends(get_db)):
    success = ExamService.remove_question_from_exam(db, exam_id, question_id)
    if not success:
        raise HTTPException(status_code=404, detail="Question not found in this exam")
    return {"message": "Question removed from exam"}