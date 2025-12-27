from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth_service import SECRET_KEY, ALGORITHM
from app.services.user_service import UserService
from app.models.user import User

# Đường dẫn API dùng để lấy token (Login)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực thông tin đăng nhập",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = UserService.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

# Hàm phụ: Chỉ cho phép Giáo viên
def get_current_teacher(user: User = Depends(get_current_user)):
    if user.role != "Teacher" and user.role != "Admin":
        raise HTTPException(status_code=403, detail="Chức năng chỉ dành cho Giáo viên")
    return user