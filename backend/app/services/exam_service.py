from sqlalchemy.orm import Session
from app.models.exam import Exam, ExamQuestion
from app.schemas.exam import ExamCreate, AddQuestionsToExam

class ExamService:
    @staticmethod
    def create_exam(db: Session, exam: ExamCreate, teacher_id: int):
        db_exam = Exam(**exam.dict(), teacher_id=teacher_id)
        db.add(db_exam)
        db.commit()
        db.refresh(db_exam)
        return db_exam

    @staticmethod
    def add_questions_to_exam(db: Session, exam_id: int, data: AddQuestionsToExam):
        # data.questions là danh sách [{question_id: 1, point_value: 5}, ...]
        for item in data.questions:
            # Kiểm tra tồn tại để tránh duplicate
            exists = db.query(ExamQuestion).filter_by(exam_id=exam_id, question_id=item.question_id).first()
            if not exists:
                link = ExamQuestion(
                    exam_id=exam_id, 
                    question_id=item.question_id, 
                    point_value=item.point_value
                )
                db.add(link)
        db.commit()
        # Trả về exam đã update
        return db.query(Exam).filter(Exam.exam_id == exam_id).first()
    # app/services/exam_service.py (Thêm vào cuối file)

    @staticmethod
    def delete_exam(db: Session, exam_id: int, teacher_id: int):
        exam = db.query(Exam).filter(Exam.exam_id == exam_id).first()
        if exam and exam.teacher_id == teacher_id:
            db.delete(exam)
            db.commit()
            return True
        return False

    @staticmethod
    def update_exam_status(db: Session, exam_id: int, status: str, teacher_id: int):
        exam = db.query(Exam).filter(Exam.exam_id == exam_id).first()
        if exam and exam.teacher_id == teacher_id:
            exam.status = status # Active, Finished...
            db.commit()
            db.refresh(exam)
            return exam
        return None