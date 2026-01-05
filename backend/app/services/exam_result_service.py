from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.models.exam_result import ExamResult
from app.models.exam_result_detail import ExamResultDetail
from app.models.question import Question
from app.models.exam_question import ExamQuestion
from app.schemas.exam_result_detail import ExamResultDetailBase

class ResultService:
    # --- CREATE (Nộp bài & Chấm điểm) ---
    @staticmethod
    def submit_exam(db: Session, exam_id: int, student_id: int, answers: List[ExamResultDetailBase]):
        # Tạo kết quả
        db_result = ExamResult(
            exam_id=exam_id,
            student_id=student_id,
            started_at=datetime.now(),
            total_score=0.0
        )
        db.add(db_result)
        db.flush()
        
        total_score = 0.0
        for ans in answers:
            # Lấy đáp án đúng và điểm
            question = db.query(Question).filter(Question.id == ans.question_id).first()
            exam_q_link = db.query(ExamQuestion).filter(
                ExamQuestion.exam_id == exam_id,
                ExamQuestion.question_id == ans.question_id
            ).first()
            
            point = exam_q_link.point if exam_q_link else 0
            
            # So sánh
            is_correct = False
            if question and question.correct_answer:
                if question.correct_answer.strip().lower() == ans.student_answer.strip().lower():
                    is_correct = True
                    total_score += point
            
            # Lưu chi tiết
            detail = ExamResultDetail(
                result_id=db_result.id,
                question_id=ans.question_id,
                student_answer=ans.student_answer,
                is_correct=is_correct
            )
            db.add(detail)
            
        db_result.total_score = total_score
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

    # --- UPDATE (Ví dụ: Giáo viên sửa điểm bằng tay) ---
    @staticmethod
    def update_result_score(db: Session, result_id: int, new_score: float):
        result = db.query(ExamResult).filter(ExamResult.id == result_id).first()
        if result:
            result.total_score = new_score
            db.commit()
            db.refresh(result)
        return result

    # --- DELETE (Hủy bài thi) ---
    @staticmethod
    def delete_result(db: Session, result_id: int):
        result = db.query(ExamResult).filter(ExamResult.id == result_id).first()
        if result:
            # Các detail sẽ tự xóa nếu cascade ở model, hoặc xóa thủ công ở đây
            db.query(ExamResultDetail).filter(ExamResultDetail.result_id == result_id).delete()
            db.delete(result)
            db.commit()
            return True
        return False