from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ExamViolation(Base):
    __tablename__ = "exam_violation"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("exam_session.id"), nullable=False, index=True)
    exam_id = Column(Integer, ForeignKey("exam.id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("student.id"), nullable=False, index=True)
    reason = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ExamSession", back_populates="violations")
    exam = relationship("Exam")
    student = relationship("Student")
