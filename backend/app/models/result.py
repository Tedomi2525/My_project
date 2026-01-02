from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class ExamAttempt(Base):
    __tablename__ = "exam_attempts"

    attempt_id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.exam_id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    
    score = Column(Float, default=0.0)
    started_at = Column(DateTime, default=datetime.now)
    submitted_at = Column(DateTime, nullable=True)

    # Quan hệ
    exam = relationship("Exam", back_populates="attempts")
    student = relationship("User", back_populates="exam_attempts")
    answers = relationship("StudentAnswer", back_populates="attempt")