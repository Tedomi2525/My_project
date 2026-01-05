from sqlalchemy.orm import Session
from app.models.question import Question
from app.schemas.question import QuestionCreate
from typing import Dict, Any

class QuestionService:
    # --- CREATE ---
    @staticmethod
    def create_question(db: Session, question_in: QuestionCreate):
        db_question = Question(**question_in.model_dump())
        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        return db_question
    
    # --- READ ---
    @staticmethod
    def get_question(db: Session, question_id: int):
        return db.query(Question).filter(Question.id == question_id).first()

    @staticmethod
    def get_questions(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Question).offset(skip).limit(limit).all()

    # --- UPDATE ---
    @staticmethod
    def update_question(db: Session, question_id: int, question_data: Dict[str, Any]):
        """
        question_data là dictionary chứa các field cần sửa.
        VD: {"content": "Câu hỏi mới", "correct_answer": "B"}
        """
        db_question = db.query(Question).filter(Question.id == question_id).first()
        if not db_question:
            return None
            
        for key, value in question_data.items():
            setattr(db_question, key, value)
            
        db.commit()
        db.refresh(db_question)
        return db_question

    # --- DELETE ---
    @staticmethod
    def delete_question(db: Session, question_id: int):
        db_question = db.query(Question).filter(Question.id == question_id).first()
        if db_question:
            db.delete(db_question)
            db.commit()
            return True
        return False