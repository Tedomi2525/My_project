from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    role: str
    full_name: str
    email: Optional[str] = None
    student_id: Optional[str] = None
