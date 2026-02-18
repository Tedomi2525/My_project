from sqlalchemy.orm import Session, joinedload

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

        print("EXAM DATA:", exam_data)
        print("QUESTIONS:", question_ids := exam_data.get("questions"))

        class_ids = exam_data.pop("class_ids", [])
        question_ids = exam_data.pop("questions", [])

        exam_data["created_by"] = owner_id

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
        return (
            db.query(Exam)
            .options(
                joinedload(Exam.allowed_classes),
                joinedload(Exam.exam_questions)
            )
            .all()
        )

    @staticmethod
    def get_exam(db: Session, exam_id: int):
        return (
            db.query(Exam)
            .options(
                joinedload(Exam.allowed_classes),
                joinedload(Exam.exam_questions)
            )
            .filter(Exam.id == exam_id)
            .first()
        )

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

        print("EXAM DATA:", exam_data)
        print("QUESTIONS:", exam_data.get("questions"))

        if not db_exam:
            return None

        # ---------- class ids ----------
        if "class_ids" in exam_data:
            new_class_ids = exam_data.pop("class_ids")
            
            # Chỉ xóa và thêm lại nếu new_class_ids là list
            if isinstance(new_class_ids, list):
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

            if isinstance(new_question_ids, list):
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
            if hasattr(db_exam, key):  # Kiểm tra attribute tồn tại
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
    
    @staticmethod
    def get_exams_for_student(
        db: Session,
        class_id: int,
    ):
        return (
            db.query(Exam)
            .join(ExamAllowedClass)
            .filter(ExamAllowedClass.class_id == class_id)
            .all()
        )
