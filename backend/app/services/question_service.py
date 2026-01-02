from sqlalchemy.orm import Session
from app import models, schemas

class QuestionService:
    @staticmethod
    def create_question(db: Session, q: schemas.QuestionCreate, teacher_id: int):
        # Logic Map: Index (0,1,2,3) -> Char ('A','B','C','D')
        index_to_char = ['A', 'B', 'C', 'D']
        correct_char = index_to_char[q.correct_answer]
        
        # Map mảng options -> cột DB
        db_question = models.Question(
            content=q.content,
            image_url=q.image_url,
            teacher_id=teacher_id,
            option_a=q.options[0],
            option_b=q.options[1],
            option_c=q.options[2] if len(q.options) > 2 else None,
            option_d=q.options[3] if len(q.options) > 3 else None,
            correct_answer=correct_char
        )
        
        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        return db_question

    @staticmethod
    def get_all_questions(db: Session):
        # Schema sẽ tự động gộp option_a,b,c,d thành list options khi trả về
        return db.query(models.Question).all()