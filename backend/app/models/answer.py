from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class StudentAnswer(Base):
    __tablename__ = "student_answers"

    answer_id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("exam_attempts.attempt_id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.question_id", ondelete="CASCADE"), nullable=False)
    
    selected_option = Column(String(1), nullable=True) # A, B, C, D (NULL nếu bỏ qua)
    is_correct = Column(Boolean, default=False)

    attempt = relationship("ExamAttempt", back_populates="answers")
    question = relationship("Question")