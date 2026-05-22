from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr


AccountRequestRole = Literal["teacher", "student"]
AccountRequestStatus = Literal["pending", "approved", "rejected"]
AccountRequestEmailStatus = Literal["pending", "sent", "failed"]


class AccountRequestCreate(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    role: AccountRequestRole
    note: Optional[str] = None


class AccountRequestResponse(AccountRequestCreate):
    id: int
    email: Optional[EmailStr] = None
    status: AccountRequestStatus
    email_status: AccountRequestEmailStatus = "pending"
    email_error: Optional[str] = None
    email_sent_at: Optional[datetime] = None
    created_account_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AccountRequestStatusResponse(BaseModel):
    id: int
    status: AccountRequestStatus
    role: AccountRequestRole
    username: Optional[str] = None
    password: Optional[str] = None
    message: str
