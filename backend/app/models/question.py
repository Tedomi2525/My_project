from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.database import Base
import enum

# 1. Định nghĩa Enum cho độ khó
class DifficultyLevel(str, enum.Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"

class Question(Base):
    __tablename__ = "question"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    question_type = Column(String(255), default="MCQ")
    
    # 2. Thêm cột phân loại độ khó (Mặc định là Dễ)
    difficulty = Column(SAEnum(DifficultyLevel), default=DifficultyLevel.EASY)
    
    options = Column(JSON, nullable=True) 
    correct_answer = Column(String(255))
    
    created_by = Column(Integer, ForeignKey("user.id"))

    exam_links = relationship("ExamQuestion", back_populates="question")