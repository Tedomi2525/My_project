from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt

from app.database import get_db
from app.services.user_service import UserService
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(tags=["Auth"])

# --- CẤU HÌNH BẢO MẬT ---
# Trong thực tế nên để cái này trong file .env
SECRET_KEY = "bi_mat_khong_duoc_bat_mi_cho_ai_biet" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 ngày

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    # 1. Tìm user trong DB
    user = UserService.get_user_by_username(db, login_data.username)
    
    # 2. Kiểm tra user có tồn tại và pass có đúng không
    if not user or not UserService.verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai tên đăng nhập hoặc mật khẩu",
        )

    # 3. Tạo Token
    access_token = create_access_token(data={"sub": user.username, "role": user.role})

    # 4. Trả về kết quả
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "role": user.role,
        "full_name": user.full_name
    }