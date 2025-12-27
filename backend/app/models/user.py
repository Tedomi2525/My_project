from sqlalchemy import Column, Integer, String, Enum, TIMESTAMP, text
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class UserRole(str, enum.Enum):

    ADMIN = "Admin"      
    TEACHER = "Teacher"
    STUDENT = "Student"

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    # Quan hệ
    # 1. Giáo viên tạo nhiều lớp
    teaching_classes = relationship("Classroom", back_populates="teacher")
    
    # 2. Sinh viên tham gia nhiều lớp (thông qua bảng trung gian)
    enrolled_classes = relationship("ClassroomMember", back_populates="student")

    # 3. Giáo viên tạo nhiều đề thi
    created_exams = relationship("Exam", back_populates="teacher")

    # 4. Sinh viên có nhiều lượt thi (kết quả)
    exam_attempts = relationship("ExamAttempt", back_populates="student")