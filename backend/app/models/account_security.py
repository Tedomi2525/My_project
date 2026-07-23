from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, UniqueConstraint

from app.database import Base


class AccountSecurity(Base):
    __tablename__ = "account_security"
    __table_args__ = (
        UniqueConstraint("role", "user_id", name="uq_account_security_role_user"),
    )

    id = Column(Integer, primary_key=True)
    role = Column(String(20), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    failed_attempts = Column(Integer, nullable=False, default=0)
    locked_until = Column(DateTime, nullable=True)
    is_locked = Column(Boolean, nullable=False, default=False)
    password_changed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
