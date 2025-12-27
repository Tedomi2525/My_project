from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.services import UserService, AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Tạo schema đơn giản cho Login
class LoginSchema(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(data: LoginSchema, db: Session = Depends(get_db)):
    # 1. Tìm user
    user = UserService.get_user_by_username(db, data.username)
    
    # 2. Check mật khẩu (vẫn dùng hàm check hash cho an toàn, hoặc so sánh == nếu bạn muốn)
    if not user or not AuthService.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Sai tài khoản hoặc mật khẩu")
    
    # 3. TRẢ VỀ LUÔN THÔNG TIN USER (Không tạo Token nữa)
    return {
        "message": "Đăng nhập thành công",
        "user_id": user.user_id,
        "username": user.username,
        "role": user.role if isinstance(user.role, str) else user.role.value
    }