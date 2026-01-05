from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class ClassStudent(Base):
    __tablename__ = "class_student"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("class.id"))
    student_id = Column(Integer, ForeignKey("user.id"))
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    class_info = relationship("Class", back_populates="students")
    student = relationship("User", back_populates="classes_joined")