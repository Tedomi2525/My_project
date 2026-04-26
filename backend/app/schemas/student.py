from typing import Optional
from pydantic import BaseModel, EmailStr, Field, model_validator


class StudentBase(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    student_id: Optional[str] = Field(None, alias="studentId")


class StudentCreate(StudentBase):
    password: Optional[str] = None


class StudentUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    student_id: Optional[str] = None


class StudentResponse(StudentBase):
    id: int
    role: str = "student"
    student_code: Optional[str] = None

    @model_validator(mode="after")
    def map_student_code_to_id(self):
        if not self.student_id and self.student_code:
            self.student_id = self.student_code
        return self

    class Config:
        from_attributes = True
        populate_by_name = True
