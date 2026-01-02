from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/exams", tags=["Exams"])

@router.get("/", response_model=List[schemas.ExamResponse])
def get_exams(db: Session = Depends(get_db)):
    # Cần logic query thêm list ID questions để trả về cho đúng Schema
    exams = db.query(models.Exam).all()
    # Demo đơn giản, thực tế cần join bảng exam_questions để lấy list ID
    return exams 

@router.get("/{exam_id}", response_model=schemas.ExamResponse) # Dành cho chi tiết đề thi
def get_exam_detail(exam_id: int, db: Session = Depends(get_db)):
     exam = db.query(models.Exam).filter(models.Exam.exam_id == exam_id).first()
     if not exam: raise HTTPException(404, "Exam not found")
     
     # Lấy danh sách ID câu hỏi để trả về frontend
     q_ids = [eq.question_id for eq in exam.questions]
     
     # Gán vào object trả về (Pydantic sẽ validate)
     exam.questions = q_ids 
     return exam

@router.post("/", response_model=schemas.ExamResponse)
def create_exam(exam_in: schemas.ExamCreate, db: Session = Depends(get_db)):
    # 1. Tạo Exam
    db_exam = models.Exam(
        title=exam_in.title,
        duration_minutes=exam_in.duration_minutes,
        start_time=exam_in.start_time,
        end_time=exam_in.end_time,
        status=exam_in.status,
        password=exam_in.password,
        show_answers=1 if exam_in.show_answers else 0,
        teacher_id=1 # Hardcode ID teacher
    )
    db.add(db_exam)
    db.commit()
    db.refresh(db_exam)
    
    # 2. Tạo liên kết câu hỏi (ExamQuestion)
    for q_id in exam_in.questions:
        link = models.ExamQuestion(
            exam_id=db_exam.exam_id,
            question_id=q_id,
            point_value=1.0 # Mặc định 1 điểm
        )
        db.add(link)
    
    # 3. Commit lần cuối
    db.commit()
    
    # Trả về kèm list ID để khớp Schema
    db_exam.questions = exam_in.questions 
    db_exam.allowed_students = exam_in.allowed_students
    return db_exam  