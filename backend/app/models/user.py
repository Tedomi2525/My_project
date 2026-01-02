from sqlalchemy import Column, Integer, String, TIMESTAMP, text
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    
    # Dùng String như bạn yêu cầu, không dùng Enum
    role = Column(String(50), nullable=False) # 'admin', 'teacher', 'student'
    
    # Thêm cột này để khớp với giao diện Admin (quản lý Mã SV)
    student_code = Column(String(20), nullable=True) 

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    # Quan hệ (Dùng chuỗi string để tránh lỗi import vòng vo)
    teaching_classes = relationship("Classroom", back_populates="teacher")
    enrolled_classes = relationship("ClassroomMember", back_populates="student")
    created_exams = relationship("Exam", back_populates="teacher")
    exam_attempts = relationship("ExamAttempt", back_populates="student")