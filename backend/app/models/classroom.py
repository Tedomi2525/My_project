from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Class(Base):
    __tablename__ = "class"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(String(255))
    teacher_id = Column(Integer, ForeignKey("user.id"))

    students = relationship(
        "ClassStudent",
        back_populates="class_",
        cascade="all, delete"
    )   
    teacher = relationship("User", back_populates="classes_created")
