from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
# from app.security import verify_password, create_access_token (Giả sử bạn đã có file security.py)

router = APIRouter(tags=["Auth"])

@router.post("/login", response_model=schemas.Token)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    # 1. Tìm user trong DB
    user = db.query(models.User).filter(models.User.username == request.username).first()
    
    # 2. Check password (demo so sánh string thô, thực tế cần hash)
    if not user or user.password_hash != request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Sai tên đăng nhập hoặc mật khẩu"
        )
    
    # 3. Tạo Token (Demo)
    return {
        "access_token": f"fake-jwt-{user.username}", # Thực tế dùng create_access_token
        "token_type": "bearer",
        "role": user.role,
        "full_name": user.full_name,
        "user_id": user.user_id
    }