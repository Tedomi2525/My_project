from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import UserService
from app.schemas.user import UserResponse, UserCreate
from app.models.user import User
from app.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

# --- DEPENDENCY PHỤ: Chỉ Admin mới được đi qua ---
def get_current_admin(user: User = Depends(get_current_user)):
    # So sánh quyền. Lưu ý: user.role là Enum, so sánh với string vẫn OK trong Python
    if user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Bạn không có quyền quản trị (Admin access required)"
        )
    return user

# =========================================================
# 1. API CHO CHÍNH USER (Ai cũng dùng được)
# =========================================================

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """Lấy thông tin của chính user đang đăng nhập (để hiển thị lên Header/Profile)"""
    return current_user

# =========================================================
# 2. API QUẢN TRỊ (Chỉ Admin dùng được)
# =========================================================

# Lấy danh sách tất cả user (Có phân trang skip/limit)
@router.get("/", response_model=List[UserResponse])
def read_all_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    admin: User = Depends(get_current_admin) # <-- Chặn quyền tại đây
):
    return UserService.get_all_users(db, skip, limit)

# Tạo tài khoản mới (Admin cấp tài khoản cho GV/SV)
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_by_admin(
    user_data: UserCreate, 
    db: Session = Depends(get_db), 
    admin: User = Depends(get_current_admin) # <-- Chặn quyền tại đây
):
    # 1. Check trùng Username
    if UserService.get_user_by_username(db, username=user_data.username):
        raise HTTPException(status_code=400, detail="Username đã tồn tại")
    
    # 2. Check trùng Email
    if UserService.get_user_by_email(db, email=user_data.email):
        raise HTTPException(status_code=400, detail="Email đã tồn tại")

    # 3. Tạo User
    return UserService.create_user(db, user_data)

# Xóa tài khoản
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    admin: User = Depends(get_current_admin) # <-- Chặn quyền tại đây
):
    # Không cho phép Admin tự xóa chính mình để tránh lỗi hệ thống
    if admin.user_id == user_id:
        raise HTTPException(status_code=400, detail="Không thể tự xóa tài khoản Admin đang đăng nhập")

    success = UserService.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User không tìm thấy")
    return None