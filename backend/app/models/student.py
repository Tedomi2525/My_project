from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Student(Base):
    __tablename__ = "student"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    full_name = Column(String(255))
    student_code = Column(String(50), unique=True, nullable=True)

    classes_joined = relationship(
        "ClassStudent",
        back_populates="student",
        cascade="all, delete"
    )

    exam_results = relationship(
        "ExamResult",
        back_populates="student"
    )

    @property
    def role(self) -> str:
        return "student"
