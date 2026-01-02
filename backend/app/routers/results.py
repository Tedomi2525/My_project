from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/submit-exam", tags=["Results"])

@router.post("/", response_model=schemas.SubmissionResult)
def submit_exam(submission: schemas.ExamSubmission, db: Session = Depends(get_db)):
    # 1. Lấy thông tin đề và câu hỏi
    exam = db.query(models.Exam).filter(models.Exam.exam_id == submission.exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Bài thi không tồn tại")
    
    # Lấy các câu hỏi trong đề để đối chiếu đáp án
    # (Cách này tối ưu hơn query từng câu)
    question_ids = [a.question_id for a in submission.answers]
    questions_db = db.query(models.Question).filter(models.Question.question_id.in_(question_ids)).all()
    
    # Tạo map để tra cứu nhanh: {question_id: 'A'}
    correct_map = {q.question_id: q.correct_answer for q in questions_db}
    
    # 2. Tính điểm
    correct_count = 0
    total_questions = len(submission.answers)
    index_to_char = ['A', 'B', 'C', 'D']

    # Tạo lượt thi (Attempt)
    db_attempt = models.ExamAttempt(
        exam_id=submission.exam_id,
        student_id=1, # Hardcode student ID
        started_at=datetime.now(), # Thực tế nên gửi từ client hoặc lấy lúc start
        submitted_at=datetime.now()
    )
    db.add(db_attempt)
    db.flush() # Để lấy attempt_id trước khi commit

    for ans in submission.answers:
        # User chọn index (-1 là không chọn)
        user_char = index_to_char[ans.selected_option_index] if ans.selected_option_index >= 0 else None
        
        # So sánh với đáp án đúng trong DB
        is_correct = False
        if user_char and user_char == correct_map.get(ans.question_id):
            correct_count += 1
            is_correct = True
            
        # Lưu chi tiết câu trả lời
        db_answer = models.StudentAnswer(
            attempt_id=db_attempt.attempt_id,
            question_id=ans.question_id,
            selected_option=user_char,
            is_correct=is_correct
        )
        db.add(db_answer)

    # 3. Tính tổng điểm (thang 10)
    final_score = 0
    if total_questions > 0:
        final_score = (correct_count / len(questions_db)) * 10
        
    db_attempt.score = final_score
    db.commit()

    return {
        "score": final_score,
        "correct_count": correct_count,
        "total_questions": len(questions_db),
        "submitted_at": db_attempt.submitted_at
    }