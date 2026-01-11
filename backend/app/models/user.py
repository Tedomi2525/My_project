from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    full_name = Column(String(255))
    role = Column(String(50), default="student")  # student | teacher

    student_code = Column(String(50), nullable=True) 


    # Student → lớp đã tham gia
    classes_joined = relationship(
        "ClassStudent",
        back_populates="student",
        cascade="all, delete"
    )

    # Teacher → lớp đã tạo
    classes_created = relationship(
        "Class",
        back_populates="teacher",
        cascade="all, delete"
    )

    # Khác
    exam_results = relationship("ExamResult", back_populates="student")
    allowed_exams = relationship("ExamAllowedStudent", back_populates="student")
