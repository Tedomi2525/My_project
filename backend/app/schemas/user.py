from pydantic import BaseModel, EmailStr
from typing import Optional


# ================= BASE =================
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: Optional[str] = "student"
    student_code: Optional[str] = None   # ✅ THÊM


# ================= CREATE =================
class UserCreate(UserBase):
    password: str   # chỉ dùng khi tạo


# ================= UPDATE =================
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    password: Optional[str] = None
    student_code: Optional[str] = None   # ✅ SỬA TÊN


# ================= LOGIN =================
class UserLogin(BaseModel):
    username: str
    password: str


# ================= RESPONSE =================
class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True   # pydantic v1
        # from_attributes = True  # nếu dùng pydantic v2
