from typing import Optional
from pydantic import BaseModel, EmailStr


class TeacherBase(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


class TeacherCreate(TeacherBase):
    password: Optional[str] = None


class TeacherUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class TeacherResponse(TeacherBase):
    id: int
    role: str = "teacher"

    class Config:
        from_attributes = True
