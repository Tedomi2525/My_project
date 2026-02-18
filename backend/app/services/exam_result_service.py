from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime

from app.models.exam_result import ExamResult
from app.models.exam_result_detail import ExamResultDetail
from app.models.question import Question
from app.models.exam_question import ExamQuestion
from app.models.exam import Exam
from app.schemas.exam_result_detail import ExamResultDetailBase


class ResultService:
    # --- CREATE (Nop bai & Cham diem) ---
    @staticmethod
    def submit_exam(db: Session, exam_id: int, student_id: int, answers: List[ExamResultDetailBase]):
        db_result = ExamResult(
            exam_id=exam_id,
            student_id=student_id,
            started_at=datetime.now(),
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
