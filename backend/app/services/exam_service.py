from sqlalchemy.orm import Session
from app.models.exam import Exam
from app.models.exam_question import ExamQuestion
from app.models.exam_allowed_class import ExamAllowedClass
from app.schemas.exam import ExamCreate


class ExamService:
    # =====================================================
    # EXAM CRUD
    # =====================================================

    @staticmethod
    def create_exam(db: Session, exam_in: ExamCreate):
        # 1. Dump data từ schema
        exam_data = exam_in.model_dump()

        class_ids = exam_data.pop("class_ids", [])
        question_ids = exam_data.pop("questions", [])

        # 2. Tạo Exam (bao gồm allow_view_answers)
        db_exam = Exam(**exam_data)
        db.add(db_exam)
        db.commit()
        db.refresh(db_exam)

        # 3. Gán lớp được phép thi
        if class_ids:
            for cls_id in class_ids:
                db.add(
                    ExamAllowedClass(
                        exam_id=db_exam.id,
                        class_id=cls_id
                    )
                )

        # 4. Gán câu hỏi vào đề
        if question_ids:
            for q_id in question_ids:
                db.add(
                    ExamQuestion(
                        exam_id=db_exam.id,
                        question_id=q_id
                    )
                )

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

        # ================= CLASS IDS =================
        if "class_ids" in exam_data:
            new_class_ids = exam_data.pop("class_ids")

            db.query(ExamAllowedClass).filter(
                ExamAllowedClass.exam_id == exam_id
            ).delete()

            if new_class_ids:
                for cls_id in new_class_ids:
                    db.add(
                        ExamAllowedClass(
                            exam_id=exam_id,
                            class_id=cls_id
                        )
                    )

        # ================= QUESTIONS =================
        if "questions" in exam_data:
            new_question_ids = exam_data.pop("questions")

            db.query(ExamQuestion).filter(
                ExamQuestion.exam_id == exam_id
            ).delete()

            if new_question_ids:
                for q_id in new_question_ids:
                    db.add(
                        ExamQuestion(
                            exam_id=exam_id,
                            question_id=q_id
                        )
                    )

        # ================= BASIC FIELDS =================
        # title, description, duration, time, password, allow_view_answers...
        for key, value in exam_data.items():
            setattr(db_exam, key, value)

        db.commit()
        db.refresh(db_exam)
        return db_exam

    @staticmethod
    def delete_exam(db: Session, exam_id: int):
        db_exam = db.query(Exam).filter(Exam.id == exam_id).first()
        if not db_exam:
            return False

        db.delete(db_exam)
        db.commit()
        return True

    # =====================================================
    # QUESTION MANAGEMENT (OPTIONAL APIs)
    # =====================================================

    @staticmethod
    def add_question_to_exam(db: Session, exam_id: int, question_id: int):
        existing = db.query(ExamQuestion).filter(
            ExamQuestion.exam_id == exam_id,
            ExamQuestion.question_id == question_id
        ).first()

        if existing:
            return existing

        db_link = ExamQuestion(
            exam_id=exam_id,
            question_id=question_id
        )
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

        if not db_link:
            return False

        db.delete(db_link)
        db.commit()
        return True
