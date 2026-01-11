from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class ClassStudent(Base):
    __tablename__ = "class_student"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("class.id", ondelete="CASCADE"))
    student_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    joined_at = Column(DateTime, default=datetime.utcnow)

    class_ = relationship("Class", back_populates="students")
    student = relationship("User", back_populates="classes_joined")
