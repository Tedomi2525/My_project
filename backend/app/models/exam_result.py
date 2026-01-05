from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class ExamResult(Base):
    __tablename__ = "exam_result"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exam.id"))
    student_id = Column(Integer, ForeignKey("user.id"))
    total_score = Column(Float, default=0.0)
    started_at = Column(DateTime(timezone=True))
    finished_at = Column(DateTime(timezone=True), server_default=func.now())

    exam = relationship("Exam", back_populates="results")
    student = relationship("User", back_populates="exam_results")
    details = relationship("ExamResultDetail", back_populates="result")