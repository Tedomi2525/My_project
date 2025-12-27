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
    # app/services/question_service.py (Thêm vào cuối file)

    @staticmethod
    def update_question(db: Session, question_id: int, data: QuestionCreate, teacher_id: int):
        # 1. Tìm câu hỏi
        question = db.query(Question).filter(Question.question_id == question_id).first()
        
        # 2. Kiểm tra tồn tại và quyền sở hữu (chỉ giáo viên tạo ra mới được sửa)
        if not question:
            return None
        if question.teacher_id != teacher_id:
            raise Exception("Permission Denied") # Hoặc xử lý lỗi ở router

        # 3. Cập nhật dữ liệu
        question.content = data.content
        question.option_a = data.option_a
        question.option_b = data.option_b
        question.option_c = data.option_c
        question.option_d = data.option_d
        question.correct_answer = data.correct_answer
        
        db.commit()
        db.refresh(question)
        return question

    @staticmethod
    def delete_question(db: Session, question_id: int, teacher_id: int):
        question = db.query(Question).filter(Question.question_id == question_id).first()
        
        if not question:
            return False
        if question.teacher_id != teacher_id:
            raise Exception("Permission Denied")

        db.delete(question)
        db.commit()
        return True