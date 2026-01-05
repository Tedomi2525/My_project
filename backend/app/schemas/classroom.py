from pydantic import BaseModel
from typing import Optional

class ClassBase(BaseModel):
    class_name: str
    description: Optional[str] = None

class ClassCreate(ClassBase):
    created_by: int # ID giáo viên

class ClassResponse(ClassBase):
    id: int
    created_by: int

    class Config:
        from_attributes = True