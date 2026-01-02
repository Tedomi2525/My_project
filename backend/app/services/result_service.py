from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException
from app import models, schemas

class ResultService:
    @staticmethod
    def submit_exam(db: Session, submission: schemas.ExamSubmission, student_id: int):
        # 1. Lấy thông tin đề thi
        exam = db.query(models.Exam).filter(models.Exam.exam_id == submission.exam_id).first()
        if not exam:
            raise HTTPException(status_code=404, detail="Bài thi không tồn tại")
        
        # 2. Lấy danh sách câu hỏi và đáp án đúng để đối chiếu
        question_ids = [a.question_id for a in submission.answers]
        questions_db = db.query(models.Question).filter(models.Question.question_id.in_(question_ids)).all()
        
        # Map: {question_id: 'A'}
        correct_map = {q.question_id: q.correct_answer for q in questions_db}
        
        # 3. Tạo lượt làm bài (Attempt)
        db_attempt = models.ExamAttempt(
            exam_id=submission.exam_id,
            student_id=student_id,
            started_at=datetime.now(), # Thực tế nên lấy từ lúc bắt đầu làm
            submitted_at=datetime.now()
        )
        db.add(db_attempt)
        db.flush() # Để có attempt_id

        # 4. Chấm điểm chi tiết từng câu
        correct_count = 0
        index_to_char = ['A', 'B', 'C', 'D']

        for ans in submission.answers:
            # Chuyển đổi Index -> Char
            user_char = None
            if ans.selected_option_index >= 0 and ans.selected_option_index < 4:
                user_char = index_to_char[ans.selected_option_index]
            
            # So sánh đáp án
            is_correct = False
            if user_char and user_char == correct_map.get(ans.question_id):
                correct_count += 1
                is_correct = True
            
            # Lưu câu trả lời (Gọi trực tiếp Model hoặc dùng AnswerService)
            db_answer = models.StudentAnswer(
                attempt_id=db_attempt.attempt_id,
                question_id=ans.question_id,
                selected_option=user_char,
                is_correct=is_correct
            )
            db.add(db_answer)

        # 5. Tính điểm tổng (Thang 10)
        total_questions = len(questions_db)
        final_score = 0.0
        if total_questions > 0:
            final_score = (correct_count / total_questions) * 10
            
        db_attempt.score = final_score
        db.commit()
        db.refresh(db_attempt)

        return {
            "score": final_score,
            "correct_count": correct_count,
            "total_questions": total_questions,
            "submitted_at": db_attempt.submitted_at
        }