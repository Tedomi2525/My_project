from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey, text
from sqlalchemy.orm import relationship
from app.database import Base

class ClassroomMember(Base):
    __tablename__ = "class_enrollments"

    class_id = Column(Integer, ForeignKey("classes.class_id", ondelete="CASCADE"), primary_key=True)
    student_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    joined_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    classroom = relationship("Classroom", back_populates="members")
    student = relationship("User", back_populates="enrolled_classes")