from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, text
from sqlalchemy.orm import relationship
from app.database import Base

class Question(Base):
    __tablename__ = "questions"

    question_id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    
    content = Column(Text, nullable=False)
    image_url = Column(String(255), nullable=True)
    
    # Lưu riêng từng phương án (Khớp với logic tách bảng)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=True)
    option_d = Column(Text, nullable=True)
    
    # Lưu đáp án đúng dạng chữ: 'A', 'B', 'C' hoặc 'D'
    correct_answer = Column(String(1), nullable=False)
    
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    # Quan hệ
    exam_links = relationship("ExamQuestion", back_populates="question")