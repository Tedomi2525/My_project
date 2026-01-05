from sqlalchemy.orm import Session
from app.models.exam import Exam
from app.models.exam_question import ExamQuestion
from app.schemas.exam import ExamCreate
from app.schemas.exam_question import ExamQuestionCreate

class ExamService:
    # === PHẦN QUẢN LÝ ĐỀ THI (EXAM) ===
    
    @staticmethod
    def create_exam(db: Session, exam_in: ExamCreate):
        db_exam = Exam(**exam_in.model_dump())
        db.add(db_exam)
        db.commit()
        db.refresh(db_exam)
        return db_exam

    @staticmethod
    def get_exam(db: Session, exam_id: int):
        return db.query(Exam).filter(Exam.id == exam_id).first()

    @staticmethod
    def get_exams(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Exam).offset(skip).limit(limit).all()

    @staticmethod
    def update_exam(db: Session, exam_id: int, exam_data: dict):
        db_exam = db.query(Exam).filter(Exam.id == exam_id).first()
        if not db_exam:
            return None
        
        for key, value in exam_data.items():
            setattr(db_exam, key, value)
            
        db.commit()
        db.refresh(db_exam)
        return db_exam

    @staticmethod
    def delete_exam(db: Session, exam_id: int):
        db_exam = db.query(Exam).filter(Exam.id == exam_id).first()
        if db_exam:
            # Lưu ý: Các bảng con (exam_question) sẽ tự xóa nếu cấu hình cascade ở app.models
            db.delete(db_exam)
            db.commit()
            return True
        return False

    # === PHẦN QUẢN LÝ CÂU HỎI TRONG ĐỀ (EXAM QUESTIONS) ===

    @staticmethod
    def add_question_to_exam(db: Session, link_in: ExamQuestionCreate):
        # Check xem đã có trong đề chưa
        existing = db.query(ExamQuestion).filter(
            ExamQuestion.exam_id == link_in.exam_id,
            ExamQuestion.question_id == link_in.question_id
        ).first()
        if existing:
            return existing 

        db_link = ExamQuestion(**link_in.model_dump())
        db.add(db_link)
        db.commit()
        db.refresh(db_link)
        return db_link

    @staticmethod
    def remove_question_from_exam(db: Session, exam_id: int, question_id: int):
        db_link = db.query(ExamQuestion).filter(
            ExamQuestion.exam_id == exam_id,
            ExamQuestion.question_id == question_id
        ).first()
        if db_link:
            db.delete(db_link)
            db.commit()
            return True
        return False