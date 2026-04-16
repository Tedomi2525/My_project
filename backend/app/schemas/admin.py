from typing import Optional
from pydantic import BaseModel, EmailStr


class AdminBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class AdminCreate(AdminBase):
    password: str


class AdminUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class AdminResponse(AdminBase):
    id: int
    role: str = "admin"

    class Config:
        from_attributes = True
