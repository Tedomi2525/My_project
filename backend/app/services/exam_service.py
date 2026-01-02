from sqlalchemy.orm import Session
from fastapi import HTTPException
from app import models, schemas

class ExamService:
    @staticmethod
    def create_exam(db: Session, exam_in: schemas.ExamCreate, teacher_id: int):
        # 1. Tạo Exam Header
        db_exam = models.Exam(
            title=exam_in.title,
            duration_minutes=exam_in.duration_minutes,
            start_time=exam_in.start_time,
            end_time=exam_in.end_time,
            status=exam_in.status,
            password=exam_in.password,
            show_answers=1 if exam_in.show_answers else 0,
            teacher_id=teacher_id
        )
        db.add(db_exam)
        db.flush() # flush để có ID ngay
        
        # 2. Tạo liên kết câu hỏi (ExamQuestion)
        for q_id in exam_in.questions:
            # Kiểm tra câu hỏi tồn tại (Optional)
            link = models.ExamQuestion(
                exam_id=db_exam.exam_id,
                question_id=q_id,
                point_value=1.0 # Mặc định 1 điểm
            )
            db.add(link)
        
        # 3. Commit
        db.commit()
        db.refresh(db_exam)
        
        # Gán lại để trả về đúng schema
        db_exam.questions = exam_in.questions
        db_exam.allowed_students = exam_in.allowed_students
        return db_exam

    @staticmethod
    def get_exam_detail(db: Session, exam_id: int):
        exam = db.query(models.Exam).filter(models.Exam.exam_id == exam_id).first()
        if not exam:
            raise HTTPException(status_code=404, detail="Đề thi không tồn tại")
        
        # Lấy danh sách ID câu hỏi để trả về frontend
        q_ids = [eq.question_id for eq in exam.questions]
        exam.questions = q_ids 
        return exam