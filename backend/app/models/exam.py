from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Exam(Base):
    __tablename__ = "exam"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    duration_minutes = Column(Integer, nullable=False)

    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)

    password = Column(String(255), nullable=True)

    created_by = Column(Integer, ForeignKey("user.id"), nullable=False)

    allow_view_answers = Column(Boolean, nullable=False, default=False)

    exam_questions = relationship(
        "ExamQuestion",
        back_populates="exam",
        cascade="all, delete-orphan"
    )

    allowed_classes = relationship(
        "ExamAllowedClass",
        back_populates="exam",
        cascade="all, delete-orphan"
    )

    # ✅ THÊM DÒNG NÀY
    results = relationship(
        "ExamResult",
        back_populates="exam",
        cascade="all, delete-orphan"
    )
