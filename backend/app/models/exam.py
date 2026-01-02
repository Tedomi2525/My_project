from sqlalchemy import Column, Integer, String, Float, TIMESTAMP, ForeignKey, Enum, text
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class ExamStatus(str, enum.Enum):
    DRAFT = "draft"      # Khớp chữ thường với Vue
    ACTIVE = "active"
    ENDED = "ended"

class Exam(Base):
    __tablename__ = "exams"

    exam_id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    
    title = Column(String(200), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    start_time = Column(TIMESTAMP, nullable=True) # Khớp với Vue: startTime
    end_time = Column(TIMESTAMP, nullable=True)   # Khớp với Vue: endTime
    
    status = Column(Enum(ExamStatus), default=ExamStatus.DRAFT)
    password = Column(String(50), nullable=True)  # Vue có tính năng mật khẩu đề thi
    show_answers = Column(Integer, default=1)     # 1: True, 0: False
    
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    # Quan hệ
    teacher = relationship("User", back_populates="created_exams")
    questions = relationship("ExamQuestion", back_populates="exam")
    attempts = relationship("ExamAttempt", back_populates="exam")

# Bảng trung gian: Đề thi - Câu hỏi
class ExamQuestion(Base):
    __tablename__ = "exam_questions"

    exam_id = Column(Integer, ForeignKey("exams.exam_id", ondelete="CASCADE"), primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.question_id", ondelete="CASCADE"), primary_key=True)
    point_value = Column(Float, default=1.0)

    exam = relationship("Exam", back_populates="questions")
    question = relationship("Question", back_populates="exam_links")