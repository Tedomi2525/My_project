from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint

from app.database import Base


class ExamStudentPolicy(Base):
    __tablename__ = "exam_student_policy"
    __table_args__ = (
        UniqueConstraint("exam_id", "student_id", name="uq_exam_student_policy"),
    )

    id = Column(Integer, primary_key=True)
    exam_id = Column(Integer, nullable=False, index=True)
    student_id = Column(Integer, nullable=False, index=True)
    extra_minutes = Column(Integer, nullable=False, default=0)
    extra_attempts = Column(Integer, nullable=False, default=0)
    session_state = Column(String(20), nullable=False, default="active")
    pause_started_at = Column(DateTime, nullable=True)
    total_paused_seconds = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

