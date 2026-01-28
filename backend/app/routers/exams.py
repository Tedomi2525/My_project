from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.exam import ExamCreate, ExamResponse, ExamUpdate
from app.schemas.exam_question import ExamQuestionCreate, ExamQuestionResponse
from app.services.exam_service import ExamService

router = APIRouter(prefix="/exams", tags=["Exams"])

# ==========================================
#               EXAM CRUD
# ==========================================

@router.post("/", response_model=ExamResponse)
def create_exam(exam: ExamCreate, db: Session = Depends(get_db)):
    """
    Tạo đề thi mới. 
    Payload exam bao gồm danh sách class_ids để gán lớp.
    """
    return ExamService.create_exam(db, exam)

@router.get("/", response_model=List[ExamResponse])
def get_exams(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Lấy danh sách đề thi.
    """
    return ExamService.get_exams(db, skip=skip, limit=limit)

@router.get("/{exam_id}", response_model=ExamResponse)
def get_exam(exam_id: int, db: Session = Depends(get_db)):
    """
    Lấy chi tiết một đề thi theo ID.
    """
    exam = ExamService.get_exam(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam

@router.put("/{exam_id}", response_model=ExamResponse)
def update_exam(
    exam_id: int, 
    exam_in: ExamUpdate, 
    db: Session = Depends(get_db)
):

    # Chuyển Schema thành dict, loại bỏ các trường user không gửi
    exam_data = exam_in.model_dump(exclude_unset=True)
    
    exam = ExamService.update_exam(db, exam_id, exam_data)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam

@router.delete("/{exam_id}")
def delete_exam(exam_id: int, db: Session = Depends(get_db)):
    """
    Xóa đề thi.
    """
    success = ExamService.delete_exam(db, exam_id)
    if not success:
         raise HTTPException(status_code=404, detail="Exam not found")
    return {"message": "Exam deleted successfully"}

# ==========================================
#        QUẢN LÝ CÂU HỎI TRONG ĐỀ
# ==========================================

@router.post("/{exam_id}/questions", response_model=ExamQuestionResponse)
def add_question_to_exam(
    exam_id: int, 
    question_link: ExamQuestionCreate, 
    db: Session = Depends(get_db)
):
    """
    Thêm một câu hỏi vào đề thi.
    """
    # Kiểm tra tính nhất quán dữ liệu (ID trên URL và ID trong body)
    if question_link.exam_id != exam_id:
        raise HTTPException(status_code=400, detail="Exam ID mismatch in payload")
        
    return ExamService.add_question_to_exam(db, question_link)

@router.delete("/{exam_id}/questions/{question_id}")
def remove_question_from_exam(
    exam_id: int, 
    question_id: int, 
    db: Session = Depends(get_db)
):
    """
    Xóa một câu hỏi khỏi đề thi.
    """
    success = ExamService.remove_question_from_exam(db, exam_id, question_id)
    if not success:
        raise HTTPException(status_code=404, detail="Question not found in this exam")
    return {"message": "Question removed from exam"}