from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: Optional[str] = "student"

class UserCreate(UserBase):
    password: str  # Chỉ khi tạo mới mới cần password

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    # Không trả về password!

    class Config:
        from_attributes = True