from sqlalchemy import Column, Integer, String, TIMESTAMP, text
from sqlalchemy.orm import relationship
from app.database import Base
# import enum  <--- BỎ DÒNG NÀY

# --- XÓA BỎ CLASS UserRole ---
# class UserRole(str, enum.Enum):
#     ADMIN = "Admin"      
#     TEACHER = "Teacher"
#     STUDENT = "Student"
# -----------------------------

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    
    # --- QUAN TRỌNG: SỬA THÀNH String(50) ---
    # Không dùng Enum nữa, dùng String để nhận mọi giá trị text
    role = Column(String(50), nullable=False) 
    # ----------------------------------------

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    # Quan hệ (Giữ nguyên)
    teaching_classes = relationship("Classroom", back_populates="teacher")
    enrolled_classes = relationship("ClassroomMember", back_populates="student")
    created_exams = relationship("Exam", back_populates="teacher")
    exam_attempts = relationship("ExamAttempt", back_populates="student")