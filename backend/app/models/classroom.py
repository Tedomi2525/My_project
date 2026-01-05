from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Class(Base):
    __tablename__ = "class" # Đã sửa thành số ít

    id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String(255))
    description = Column(String(255), nullable=True)
    created_by = Column(Integer, ForeignKey("user.id")) # Link tới bảng user

    students = relationship("ClassStudent", back_populates="class_info")