from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"

# --- Login & Token ---
class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    full_name: str
    user_id: int

# --- User CRUD ---
class UserBase(BaseModel):
    username: str
    full_name: str
    email: EmailStr
    role: Role
    # Vue gửi 'studentId', Backend map vào 'student_code'
    student_code: Optional[str] = Field(None, alias="studentId")

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True # Cho phép trả về field alias (studentId)