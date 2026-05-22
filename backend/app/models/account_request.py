from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database import Base


class AccountRequest(Base):
    __tablename__ = "account_request"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True, index=True)
    role = Column(String(20), nullable=False)
    note = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="pending", index=True)
    created_account_id = Column(Integer, nullable=True)
    email_status = Column(String(20), nullable=False, default="pending")
    email_error = Column(Text, nullable=True)
    email_sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
