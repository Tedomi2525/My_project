from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class ExamAllowedClass(Base):
    __tablename__ = "exam_allowed_class"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exam.id"))
    class_id = Column(Integer, ForeignKey("class.id")) 

    exam = relationship("Exam", back_populates="allowed_classes")
