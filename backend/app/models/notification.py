from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, UniqueConstraint

from app.database import Base


class Notification(Base):
    __tablename__ = "notification"
    __table_args__ = (
        UniqueConstraint("student_id", "notification_key", name="uq_notification_student_key"),
    )

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, nullable=False, index=True)
    notification_key = Column(String(160), nullable=False)
    notification_type = Column(String(30), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    entity_type = Column(String(30), nullable=True)
    entity_id = Column(Integer, nullable=True)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

