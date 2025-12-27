from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.user import UserRole # Import Enum từ Model

# Base: Các trường chung
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.STUDENT

# Create: Dùng khi đăng ký/tạo user (Cần mật khẩu)
class UserCreate(UserBase):
    password: str

# Update: Dùng khi sửa profile (Các trường đều không bắt buộc)
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

# Response: Trả về Client (Không bao giờ trả về password!)
class UserResponse(UserBase):
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True