from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class ExamQuestion(Base):
    __tablename__ = "exam_question"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exam.id"))
    question_id = Column(Integer, ForeignKey("question.id"))
    point = Column(Integer, default=1)

    exam = relationship("Exam", back_populates="exam_questions")
    question = relationship("Question", back_populates="exam_links")