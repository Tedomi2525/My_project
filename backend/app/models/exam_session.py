from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ExamSession(Base):
    __tablename__ = "exam_session"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exam.id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("student.id"), nullable=False, index=True)
    answers = Column(JSON, nullable=False, default=dict)
    violation_count = Column(Integer, nullable=False, default=0)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    last_saved_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    submitted_at = Column(DateTime(timezone=True), nullable=True)

    exam = relationship("Exam")
    student = relationship("Student")
    violations = relationship(
        "ExamViolation",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    @property
    def session_id(self) -> int:
        return self.id
