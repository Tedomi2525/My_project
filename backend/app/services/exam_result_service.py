from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, case
from typing import List
from datetime import datetime
from fastapi import HTTPException, status

from app.models.exam_result import ExamResult
from app.models.exam_result_detail import ExamResultDetail
from app.models.question import Question, DifficultyLevel
from app.models.exam_question import ExamQuestion
from app.models.exam import Exam
from app.models.exam_allowed_class import ExamAllowedClass
from app.models.class_student import ClassStudent
from app.models.exam_session import ExamSession
from app.schemas.exam_result_detail import ExamResultDetailBase


class ResultService:
    # --- CREATE (Nop bai & Cham diem) ---
    @staticmethod
    def submit_exam(
        db: Session,
        exam_id: int,
        student_id: int,
        answers: List[ExamResultDetailBase],
        password: str | None = None,
    ):
        exam = db.query(Exam).filter(Exam.id == exam_id).first()
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam not found"
            )

        has_class_access = (
            db.query(ExamAllowedClass)
            .join(ClassStudent, ClassStudent.class_id == ExamAllowedClass.class_id)
            .filter(
                ExamAllowedClass.exam_id == exam_id,
                ClassStudent.student_id == student_id,
            )
            .first()
            is not None
        )
        if not has_class_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this exam"
            )

        now = datetime.now()
        start_time = exam.start_time.replace(tzinfo=None) if exam.start_time else None
        end_time = exam.end_time.replace(tzinfo=None) if exam.end_time else None
        if start_time and now < start_time:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Exam has not started yet"
            )
        if end_time and now > end_time:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Exam has ended"
            )

        if exam.password and exam.password != (password or ""):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Wrong exam password"
            )

        if exam.max_attempts is not None:
            attempt_count = (
                db.query(ExamResult)
                .filter(
                    ExamResult.exam_id == exam_id,
                    ExamResult.student_id == student_id
                )
                .count()
            )
            if attempt_count >= exam.max_attempts:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Attempt limit reached ({exam.max_attempts})"
                )

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
        started_at = session.started_at if session else datetime.now()

        db_result = ExamResult(
            exam_id=exam_id,
            student_id=student_id,
            started_at=started_at,
            total_score=0.0
        )
        db.add(db_result)
        db.flush()

        exam_question_links = db.query(ExamQuestion).filter(ExamQuestion.exam_id == exam_id).all()
        exam_question_ids = {link.question_id for link in exam_question_links}
        total_questions = len(exam_question_ids)

        correct_count = 0

        for ans in answers:
            if ans.question_id not in exam_question_ids:
                continue

            question = db.query(Question).filter(Question.id == ans.question_id).first()

            is_correct = False
            if question and question.correct_answer:
                if question.correct_answer.strip().lower() == ans.student_answer.strip().lower():
                    is_correct = True
                    correct_count += 1

            detail = ExamResultDetail(
                result_id=db_result.id,
                question_id=ans.question_id,
                student_answer=ans.student_answer,
                is_correct=is_correct
            )
            db.add(detail)

        db_result.total_score = (correct_count / total_questions) * 10 if total_questions > 0 else 0.0
        if session:
            session.submitted_at = datetime.now()
            session.answers = {
                str(ans.question_id): ans.student_answer
                for ans in answers
                if ans.question_id in exam_question_ids
            }
            session.last_saved_at = datetime.now()
        db.commit()
        db.refresh(db_result)
        return db_result

    # --- READ ---
    @staticmethod
    def get_result(db: Session, result_id: int):
        return db.query(ExamResult).filter(ExamResult.id == result_id).first()

    @staticmethod
    def get_student_history(db: Session, student_id: int):
        return db.query(ExamResult).filter(ExamResult.student_id == student_id).all()

    @staticmethod
    def get_exam_results_for_teacher(db: Session, exam_id: int, teacher_id: int):
        exam = db.query(Exam).filter(Exam.id == exam_id).first()
        if not exam or exam.created_by != teacher_id:
            return None

        results = (
            db.query(ExamResult)
            .options(joinedload(ExamResult.student))
            .filter(ExamResult.exam_id == exam_id)
            .order_by(ExamResult.finished_at.desc())
            .all()
        )

        return [
            {
                "id": r.id,
                "exam_id": r.exam_id,
                "student_id": r.student_id,
                "student_name": r.student.full_name if r.student else f"Student #{r.student_id}",
                "student_code": r.student.student_code if r.student and r.student.student_code else "",
                "total_score": r.total_score,
                "started_at": r.started_at,
                "finished_at": r.finished_at,
            }
            for r in results
        ]

    @staticmethod
    def get_result_review(db: Session, result_id: int):
        result = (
            db.query(ExamResult)
            .options(
                joinedload(ExamResult.exam),
                joinedload(ExamResult.details).joinedload(ExamResultDetail.question)
            )
            .filter(ExamResult.id == result_id)
            .first()
        )
        if not result:
            return None

        question_links = (
            db.query(ExamQuestion)
            .options(joinedload(ExamQuestion.question))
            .filter(ExamQuestion.exam_id == result.exam_id)
            .order_by(ExamQuestion.id.asc())
            .all()
        )

        detail_by_question_id = {d.question_id: d for d in result.details}
        questions = []
        for link in question_links:
            q = link.question
            if not q:
                continue

            detail = detail_by_question_id.get(q.id)
            questions.append(
                {
                    "question_id": q.id,
                    "content": q.content,
                    "difficulty": q.difficulty.value if q.difficulty else None,
                    "options": q.options,
                    "correct_answer": q.correct_answer,
                    "student_answer": detail.student_answer if detail else "",
                    "is_correct": detail.is_correct if detail else False,
                }
            )

        return {
            "result_id": result.id,
            "exam_id": result.exam_id,
            "exam_title": result.exam.title if result.exam else f"Exam #{result.exam_id}",
            "student_id": result.student_id,
            "total_score": result.total_score,
            "started_at": result.started_at,
            "finished_at": result.finished_at,
            "allow_view_answers": result.exam.allow_view_answers if result.exam else False,
            "questions": questions,
        }

    @staticmethod
    def get_student_difficulty_stats(db: Session, student_id: int):
        rows = (
            db.query(
                Question.difficulty,
                func.count(ExamResultDetail.id).label("attempted"),
                func.sum(
                    case(
                        (ExamResultDetail.is_correct.is_(False), 1),
                        else_=0
                    )
                ).label("wrong")
            )
            .join(ExamResultDetail, ExamResultDetail.question_id == Question.id)
            .join(ExamResult, ExamResultDetail.result_id == ExamResult.id)
            .filter(ExamResult.student_id == student_id)
            .group_by(Question.difficulty)
            .all()
        )

        stats_by_diff = {
            level.value: {
                "difficulty": level.value,
                "attempted": 0,
                "wrong": 0,
                "wrong_rate": 0.0,
            }
            for level in DifficultyLevel
        }

        total_attempted = 0
        total_wrong = 0

        for diff, attempted, wrong in rows:
            key = diff.value if diff else "UNKNOWN"
            if key not in stats_by_diff:
                stats_by_diff[key] = {
                    "difficulty": key,
                    "attempted": 0,
                    "wrong": 0,
                    "wrong_rate": 0.0,
                }

            attempted_count = int(attempted or 0)
            wrong_count = int(wrong or 0)

            stats_by_diff[key]["attempted"] = attempted_count
            stats_by_diff[key]["wrong"] = wrong_count
            stats_by_diff[key]["wrong_rate"] = (
                wrong_count / attempted_count if attempted_count > 0 else 0.0
            )

            total_attempted += attempted_count
            total_wrong += wrong_count

        return {
            "student_id": student_id,
            "total_attempted": total_attempted,
            "total_wrong": total_wrong,
            "by_difficulty": list(stats_by_diff.values()),
        }

    # --- UPDATE (Vi du: Giao vien sua diem bang tay) ---
    @staticmethod
    def update_result_score(db: Session, result_id: int, new_score: float):
        result = db.query(ExamResult).filter(ExamResult.id == result_id).first()
        if result:
            result.total_score = new_score
            db.commit()
            db.refresh(result)
        return result

    # --- DELETE (Huy bai thi) ---
    @staticmethod
    def delete_result(db: Session, result_id: int):
        result = db.query(ExamResult).filter(ExamResult.id == result_id).first()
        if result:
            db.query(ExamResultDetail).filter(ExamResultDetail.result_id == result_id).delete()
            db.delete(result)
            db.commit()
            return True
        return False

    @staticmethod
    def get_question_analytics_for_teacher(db: Session, exam_id: int, teacher_id: int):
        exam = db.query(Exam).filter(Exam.id == exam_id).first()
        if not exam or exam.created_by != teacher_id:
            return None

        questions = (
            db.query(Question)
            .join(ExamQuestion, Question.id == ExamQuestion.question_id)
            .filter(ExamQuestion.exam_id == exam_id)
            .order_by(ExamQuestion.id.asc())
            .all()
        )

        rows = (
            db.query(
                ExamResultDetail.question_id,
                func.count(ExamResultDetail.id).label("total"),
                func.sum(
                    case(
                        (ExamResultDetail.is_correct.is_(True), 1),
                        else_=0,
                    )
                ).label("correct"),
            )
            .join(ExamResult, ExamResult.id == ExamResultDetail.result_id)
            .filter(ExamResult.exam_id == exam_id)
            .group_by(ExamResultDetail.question_id)
            .all()
        )
        stats = {
            question_id: {
                "total": int(total or 0),
                "correct": int(correct or 0),
            }
            for question_id, total, correct in rows
        }

        result = []
        for question in questions:
            stat = stats.get(question.id, {"total": 0, "correct": 0})
            total = stat["total"]
            correct = stat["correct"]
            wrong = max(total - correct, 0)
            correct_rate = correct / total if total else 0.0
            result.append(
                {
                    "question_id": question.id,
                    "content": question.content,
                    "difficulty": question.difficulty.value if question.difficulty else None,
                    "total_answers": total,
                    "correct_answers": correct,
                    "wrong_answers": wrong,
                    "correct_rate": correct_rate,
                    "wrong_rate": wrong / total if total else 0.0,
                }
            )

        return result
