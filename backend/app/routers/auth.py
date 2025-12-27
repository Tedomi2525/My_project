from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import AuthService, UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    API Đăng nhập:
    - Nhận vào: username, password (qua Form-data)
    - Trả về: Access Token để kẹp vào Header các request sau
    """
    
    # 1. Tìm user trong DB theo username
    user = UserService.get_user_by_username(db, form_data.username)
    
    # 2. Kiểm tra user có tồn tại không VÀ mật khẩu có khớp không
    if not user or not AuthService.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai tên đăng nhập hoặc mật khẩu",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Nếu đúng hết -> Tạo Token
    access_token = AuthService.create_access_token(data={"sub": user.username})
    
    # 4. Trả về Token kèm thông tin Role (để Frontend biết đường điều hướng)
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "role": user.role  # Frontend dùng cái này để redirect: Admin -> Dashboard, Student -> Exam list
    }