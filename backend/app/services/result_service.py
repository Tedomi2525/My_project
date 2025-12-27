from sqlalchemy.orm import Session
from datetime import datetime
from app.models.result import ExamAttempt
from app.models.answer import StudentAnswer
from app.models.question import Question
from app.models.exam import ExamQuestion
from app.schemas.result import SubmitExamRequest

class ResultService:
    @staticmethod
    def start_exam(db: Session, exam_id: int, student_id: int):
        # Tạo lượt thi mới
        attempt = ExamAttempt(exam_id=exam_id, student_id=student_id)
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
        return attempt

    @staticmethod
    def submit_exam(db: Session, attempt_id: int, submission: SubmitExamRequest):
        """
        Logic chấm điểm:
        1. Lấy lượt thi (attempt)
        2. Lấy danh sách câu hỏi và điểm số cấu hình của đề thi đó
        3. Duyệt qua từng câu trả lời của sinh viên:
           - So khớp đáp án đúng trong bảng Question
           - Nếu đúng -> Cộng điểm dựa trên bảng ExamQuestion
           - Lưu vào bảng StudentAnswer
        4. Cập nhật tổng điểm vào ExamAttempt
        """
        attempt = db.query(ExamAttempt).filter(ExamAttempt.attempt_id == attempt_id).first()
        if not attempt:
            return None

        total_score = 0.0
        
        # Lấy cấu hình điểm số cho từng câu hỏi trong đề này
        # Key: question_id, Value: point_value
        exam_questions = db.query(ExamQuestion).filter(ExamQuestion.exam_id == attempt.exam_id).all()
        points_map = {eq.question_id: eq.point_value for eq in exam_questions}

        for ans in submission.answers:
            # Lấy thông tin câu hỏi gốc để biết đáp án đúng
            question = db.query(Question).filter(Question.question_id == ans.question_id).first()
            
            is_correct = False
            if question and question.correct_answer == ans.selected_option:
                is_correct = True
                # Cộng điểm nếu câu hỏi này có trong đề (an toàn dữ liệu)
                total_score += points_map.get(question.question_id, 0)

            # Lưu câu trả lời vào DB
            student_answer = StudentAnswer(
                attempt_id=attempt_id,
                question_id=ans.question_id,
                selected_option=ans.selected_option,
                is_correct=is_correct
            )
            db.add(student_answer)

        # Cập nhật kết quả cuối cùng
        attempt.score = total_score
        attempt.submitted_at = datetime.utcnow()
        
        db.commit()
        db.refresh(attempt)
        return attempt
    @staticmethod
    def get_results_by_exam(db: Session, exam_id: int):
        # Lấy tất cả lượt thi của đề này
        return db.query(ExamAttempt).filter(ExamAttempt.exam_id == exam_id).all()