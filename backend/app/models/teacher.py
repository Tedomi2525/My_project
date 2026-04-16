from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Teacher(Base):
    __tablename__ = "teacher"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    full_name = Column(String(255))

    classes_created = relationship(
        "Class",
        back_populates="teacher",
        cascade="all, delete"
    )

    @property
    def role(self) -> str:
        return "teacher"
