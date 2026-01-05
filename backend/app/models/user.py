from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "user"  # Đã sửa thành số ít

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    full_name = Column(String(255))
    role = Column(String(255), default="student") 

    # Quan hệ
    classes_joined = relationship("ClassStudent", back_populates="student")
    exam_results = relationship("ExamResult", back_populates="student")
    allowed_exams = relationship("ExamAllowedStudent", back_populates="student")