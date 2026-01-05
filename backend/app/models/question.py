from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Question(Base):
    __tablename__ = "question"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    question_type = Column(String(255), default="MCQ")
    options = Column(JSON, nullable=True) 
    correct_answer = Column(String(255))
    
    created_by = Column(Integer, ForeignKey("user.id"))

    exam_links = relationship("ExamQuestion", back_populates="question")