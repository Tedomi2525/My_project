from sqlalchemy.orm import Session
from app.models.question import Question
from app.schemas.question import QuestionCreate

class QuestionService:
    @staticmethod
    def create_question(db: Session, question: QuestionCreate, teacher_id: int):
        db_question = Question(**question.dict(), teacher_id=teacher_id)
        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        return db_question

    @staticmethod
    def get_questions_by_teacher(db: Session, teacher_id: int):
        return db.query(Question).filter(Question.teacher_id == teacher_id).all()