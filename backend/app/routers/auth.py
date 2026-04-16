from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt

from app.database import get_db
from app.services.account_service import AccountService
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(tags=["Auth"])

SECRET_KEY = "bi_mat_khong_duoc_bat_mi_cho_ai_biet"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    account = AccountService.find_by_username(db, login_data.username)

    if not account or not AccountService.verify_password(login_data.password, account.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai tên đăng nhập hoặc mật khẩu",
        )

    access_token = create_access_token(
        data={
            "sub": account.username,
            "role": account.role,
            "user_id": account.id,
            "username": account.username,
            "full_name": account.full_name,
            "email": getattr(account, "email", None),
            "student_id": getattr(account, "student_code", None)
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": account.id,
        "role": account.role,
        "full_name": account.full_name,
        "email": getattr(account, "email", None),
        "student_id": getattr(account, "student_code", None)
    }
