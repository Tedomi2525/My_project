from sqlalchemy import Column, Integer, String, Float, TIMESTAMP, ForeignKey, Enum, text
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class ExamStatus(str, enum.Enum):
    DRAFT = "Draft"
    ACTIVE = "Active"
    FINISHED = "Finished"

class Exam(Base):
    __tablename__ = "exams"

    exam_id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    status = Column(Enum(ExamStatus), default=ExamStatus.DRAFT)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    # Quan hệ
    teacher = relationship("User", back_populates="created_exams")
    # Liên kết với câu hỏi thông qua bảng trung gian ExamQuestion
    questions = relationship("ExamQuestion", back_populates="exam")
    # Các lượt làm bài của sinh viên
    attempts = relationship("ExamAttempt", back_populates="exam")

class ExamQuestion(Base):
    __tablename__ = "exam_questions"

    exam_id = Column(Integer, ForeignKey("exams.exam_id", ondelete="CASCADE"), primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.question_id", ondelete="CASCADE"), primary_key=True)
    point_value = Column(Float, default=1.0)

    # Quan hệ
    exam = relationship("Exam", back_populates="questions")
    question = relationship("Question", back_populates="exam_links")