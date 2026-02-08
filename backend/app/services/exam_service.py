from sqlalchemy.orm import Session

from app.models.exam import Exam
from app.models.exam_question import ExamQuestion
from app.models.exam_allowed_class import ExamAllowedClass
from app.models.question import Question

from app.schemas.exam import ExamCreate


class ExamService:
    # =====================================================
    # EXAM CRUD (NO AUTH / NO ROLE)
    # =====================================================

    @staticmethod
    def create_exam(
        db: Session,
        exam_in: ExamCreate,
        owner_id: int,
    ):
        exam_data = exam_in.model_dump()

        class_ids = exam_data.pop("class_ids", [])
        question_ids = exam_data.pop("questions", [])

        exam_data["owner_id"] = owner_id

        db_exam = Exam(**exam_data)
        db.add(db_exam)
        db.commit()
        db.refresh(db_exam)

        # allowed classes
        for cls_id in class_ids:
            db.add(
                ExamAllowedClass(
                    exam_id=db_exam.id,
                    class_id=cls_id
                )
            )

        # questions
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

    # =====================================================
    # READ
    # =====================================================

    @staticmethod
    def get_exams(db: Session):
        return db.query(Exam).all()

    @staticmethod
    def get_exam(db: Session, exam_id: int):
        return db.query(Exam).filter(
            Exam.id == exam_id
        ).first()

    # =====================================================
    # UPDATE / DELETE
    # =====================================================

    @staticmethod
    def update_exam(
        db: Session,
        exam_id: int,
        exam_data: dict,
    ):
        db_exam = db.query(Exam).filter(
            Exam.id == exam_id
        ).first()

        if not db_exam:
            return None

        # ---------- class ids ----------
        if "class_ids" in exam_data:
            new_class_ids = exam_data.pop("class_ids")

            db.query(ExamAllowedClass).filter(
                ExamAllowedClass.exam_id == exam_id
            ).delete()

            for cls_id in new_class_ids:
                db.add(
                    ExamAllowedClass(
                        exam_id=exam_id,
                        class_id=cls_id
                    )
                )

        # ---------- questions ----------
        if "questions" in exam_data:
            new_question_ids = exam_data.pop("questions")

            db.query(ExamQuestion).filter(
                ExamQuestion.exam_id == exam_id
            ).delete()

            for q_id in new_question_ids:
                db.add(
                    ExamQuestion(
                        exam_id=exam_id,
                        question_id=q_id
                    )
                )

        # ---------- basic fields ----------
        for key, value in exam_data.items():
            setattr(db_exam, key, value)

        db.commit()
        db.refresh(db_exam)
        return db_exam

    @staticmethod
    def delete_exam(
        db: Session,
        exam_id: int,
    ):
        db_exam = db.query(Exam).filter(
            Exam.id == exam_id
        ).first()

        if not db_exam:
            return False

        db.delete(db_exam)
        db.commit()
        return True

    # =====================================================
    # QUESTION MANAGEMENT
    # =====================================================

    @staticmethod
    def add_question_to_exam(
        db: Session,
        exam_id: int,
        question_id: int,
    ):
        exam = db.query(Exam).filter(
            Exam.id == exam_id
        ).first()

        if not exam:
            return None

        exists = db.query(ExamQuestion).filter(
            ExamQuestion.exam_id == exam_id,
            ExamQuestion.question_id == question_id
        ).first()

        if exists:
            return exists

        link = ExamQuestion(
            exam_id=exam_id,
            question_id=question_id
        )
        db.add(link)
        db.commit()
        db.refresh(link)
        return link

    @staticmethod
    def remove_question_from_exam(
        db: Session,
        exam_id: int,
        question_id: int,
    ):
        link = db.query(ExamQuestion).filter(
            ExamQuestion.exam_id == exam_id,
            ExamQuestion.question_id == question_id
        ).first()

        if not link:
            return False

        db.delete(link)
        db.commit()
        return True

    @staticmethod
    def get_exam_questions(
        db: Session,
        exam_id: int,
    ):
        return (
            db.query(Question)
            .join(ExamQuestion, Question.id == ExamQuestion.question_id)
            .filter(ExamQuestion.exam_id == exam_id)
            .all()
        )
