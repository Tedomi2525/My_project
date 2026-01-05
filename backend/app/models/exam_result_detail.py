from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class ExamResultDetail(Base):
    __tablename__ = "exam_result_detail"

    id = Column(Integer, primary_key=True, index=True)
    result_id = Column(Integer, ForeignKey("exam_result.id"))
    question_id = Column(Integer, ForeignKey("question.id"))
    student_answer = Column(String(255))
    is_correct = Column(Boolean, default=False)

    result = relationship("ExamResult", back_populates="details")
    question = relationship("Question")