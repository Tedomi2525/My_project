from sqlalchemy.orm import Session
from app import models

class AnswerService:
    @staticmethod
    def save_student_answer(db: Session, attempt_id: int, question_id: int, selected_char: str, is_correct: bool):
        db_answer = models.StudentAnswer(
            attempt_id=attempt_id,
            question_id=question_id,
            selected_option=selected_char,
            is_correct=is_correct
        )
        db.add(db_answer)
        return db_answer