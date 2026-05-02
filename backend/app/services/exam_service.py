from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from fastapi import HTTPException, status

from app.models.exam import Exam
from app.models.exam_question import ExamQuestion
from app.models.exam_allowed_class import ExamAllowedClass
from app.models.exam_result import ExamResult
from app.models.exam_session import ExamSession
from app.models.exam_violation import ExamViolation
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

    @staticmethod
    def check_exam_password(
        db: Session,
        exam_id: int,
        password: str,
    ) -> bool:
        exam = db.query(Exam).filter(Exam.id == exam_id).first()
        if not exam:
            return False

        if not exam.password:
            return True

        return exam.password == password

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

        has_results = (
            db.query(ExamResult)
            .filter(ExamResult.exam_id == exam_id)
            .first()
            is not None
        )
        protected_fields = {
            "duration_minutes",
            "start_time",
            "end_time",
            "class_ids",
            "questions",
            "shuffle_questions",
            "shuffle_options",
        }
        if has_results and any(field in exam_data for field in protected_fields):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change exam structure after submissions exist",
            )

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
                # Normalize: unique IDs, keep original order
                normalized_question_ids = list(dict.fromkeys(new_question_ids))

                if has_results:
                    # Preserve historic structure for exams that already have attempts:
                    # only append new questions, do not wipe old links.
                    existing_ids = {
                        row[0]
                        for row in db.query(ExamQuestion.question_id)
                        .filter(ExamQuestion.exam_id == exam_id)
                        .all()
                    }
                    ids_to_add = [q_id for q_id in normalized_question_ids if q_id not in existing_ids]

                    for q_id in ids_to_add:
                        db.add(
                            ExamQuestion(
                                exam_id=exam_id,
                                question_id=q_id
                            )
                        )
                else:
                    db.query(ExamQuestion).filter(
                        ExamQuestion.exam_id == exam_id
                    ).delete()

                    for q_id in normalized_question_ids:
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
    def set_status(db: Session, exam_id: int, status_value: str):
        if status_value not in {"draft", "published", "closed"}:
            raise HTTPException(status_code=400, detail="Invalid exam status")

        exam = db.query(Exam).filter(Exam.id == exam_id).first()
        if not exam:
            return None

        if status_value == "published":
            question_count = (
                db.query(ExamQuestion)
                .filter(ExamQuestion.exam_id == exam_id)
                .count()
            )
            class_count = (
                db.query(ExamAllowedClass)
                .filter(ExamAllowedClass.exam_id == exam_id)
                .count()
            )
            if question_count <= 0 or class_count <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="Exam needs at least one question and one class before publishing",
                )

        exam.status = status_value
        db.commit()
        db.refresh(exam)
        return exam

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
            .order_by(ExamQuestion.id.asc())
            .all()
        )
    
    @staticmethod
    def get_exams_for_student(
        db: Session,
        class_ids: int | list[int],
    ):
        if isinstance(class_ids, int):
            class_id_list = [class_ids]
        else:
            class_id_list = list(dict.fromkeys(class_ids))

        if not class_id_list:
            return []

        return (
            db.query(Exam)
            .join(ExamAllowedClass)
            .filter(
                ExamAllowedClass.class_id.in_(class_id_list),
                Exam.status == "published",
            )
            .distinct()
            .all()
        )

    @staticmethod
    def _get_or_create_session(db: Session, exam_id: int, student_id: int):
        session = (
            db.query(ExamSession)
            .filter(
                ExamSession.exam_id == exam_id,
                ExamSession.student_id == student_id,
                ExamSession.submitted_at.is_(None),
            )
            .order_by(ExamSession.id.desc())
            .first()
        )
        if session:
            return session

        session = ExamSession(
            exam_id=exam_id,
            student_id=student_id,
            answers={},
            violation_count=0,
            started_at=datetime.now(),
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def start_exam_session(db: Session, exam_id: int, student_id: int):
        exam = db.query(Exam).filter(Exam.id == exam_id).first()
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        if exam.status != "published":
            raise HTTPException(status_code=403, detail="Exam is not published")

        now = datetime.now()
        if exam.start_time and now < exam.start_time.replace(tzinfo=None):
            raise HTTPException(status_code=403, detail="Exam has not started yet")
        if exam.end_time and now > exam.end_time.replace(tzinfo=None):
            raise HTTPException(status_code=403, detail="Exam has ended")

        if exam.max_attempts is not None:
            attempt_count = (
                db.query(ExamResult)
                .filter(
                    ExamResult.exam_id == exam_id,
                    ExamResult.student_id == student_id,
                )
                .count()
            )
            if attempt_count >= exam.max_attempts:
                raise HTTPException(
                    status_code=400,
                    detail=f"Attempt limit reached ({exam.max_attempts})",
                )

        return ExamService._get_or_create_session(db, exam_id, student_id)

    @staticmethod
    def autosave_exam_session(db: Session, exam_id: int, student_id: int, answers: dict):
        session = ExamService._get_or_create_session(db, exam_id, student_id)
        session.answers = {str(key): value for key, value in answers.items()}
        session.last_saved_at = datetime.now()
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def log_violation(db: Session, exam_id: int, student_id: int, reason: str):
        session = ExamService._get_or_create_session(db, exam_id, student_id)
        violation = ExamViolation(
            session_id=session.id,
            exam_id=exam_id,
            student_id=student_id,
            reason=reason,
        )
        session.violation_count = (session.violation_count or 0) + 1
        session.last_saved_at = datetime.now()
        db.add(violation)
        db.commit()
        db.refresh(violation)
        return violation

    @staticmethod
    def get_exam_sessions_for_teacher(db: Session, exam_id: int, teacher_id: int):
        exam = db.query(Exam).filter(Exam.id == exam_id).first()
        if not exam or exam.created_by != teacher_id:
            return None

        return (
            db.query(ExamSession)
            .options(joinedload(ExamSession.violations))
            .filter(ExamSession.exam_id == exam_id)
            .order_by(ExamSession.started_at.desc())
            .all()
        )
