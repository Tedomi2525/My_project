from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Exam(Base):
    __tablename__ = "exam"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer)
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(Integer, ForeignKey("user.id"))

    exam_questions = relationship("ExamQuestion", back_populates="exam")
    allowed_students = relationship("ExamAllowedStudent", back_populates="exam")
    results = relationship("ExamResult", back_populates="exam")