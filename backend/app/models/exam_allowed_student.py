from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class ExamAllowedStudent(Base):
    __tablename__ = "exam_allowed_student"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exam.id"))
    student_id = Column(Integer, ForeignKey("user.id"))

    exam = relationship("Exam", back_populates="allowed_students")
    student = relationship("User", back_populates="allowed_exams")