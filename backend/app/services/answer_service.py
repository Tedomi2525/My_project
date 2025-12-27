from sqlalchemy.orm import Session
from app.models.answer import StudentAnswer

class AnswerService:
    @staticmethod
    def save_single_answer(db: Session, attempt_id: int, question_id: int, selected_option: str):
        # Tìm xem đã trả lời câu này chưa, nếu có rồi thì update, chưa thì insert
        existing_answer = db.query(StudentAnswer).filter_by(attempt_id=attempt_id, question_id=question_id).first()
        
        if existing_answer:
            existing_answer.selected_option = selected_option
            # Lưu ý: Logic check đúng sai có thể làm ở đây hoặc để lúc nộp bài tính sau
        else:
            new_answer = StudentAnswer(
                attempt_id=attempt_id, 
                question_id=question_id, 
                selected_option=selected_option
            )
            db.add(new_answer)
            
        db.commit()
        return True