from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User

# -------------------------------------------------------------------
# 1. Dependency lấy User hiện tại từ Header (Thay cho Token)
# -------------------------------------------------------------------
def get_current_user(
    # FastAPI sẽ tự tìm header tên là "x-user-id"
    x_user_id: str = Header(..., description="ID của người dùng đang đăng nhập"), 
    db: Session = Depends(get_db)
):
    """
    Hàm này thay thế cho việc giải mã JWT.
    Nó nhận user_id trực tiếp từ Header của request.
    """
    try:
        user_id_int = int(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Header x-user-id phải là số nguyên"
        )

    # Tìm user trong DB
    user = db.query(User).filter(User.user_id == user_id_int).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User ID không tồn tại hoặc không hợp lệ"
        )
    
    return user

# -------------------------------------------------------------------
# 2. Dependency kiểm tra quyền Giáo viên
# -------------------------------------------------------------------
def get_current_teacher(current_user: User = Depends(get_current_user)):
    # Lấy role ra (xử lý cả trường hợp nó là Enum hoặc String để tránh lỗi)
    role_name = current_user.role.value if hasattr(current_user.role, "value") else current_user.role
    
    # Cho phép cả Admin và Teacher
    if role_name not in ["Teacher", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Bạn không có quyền Giáo viên (Role required: Teacher/Admin)"
        )
    return current_user

# -------------------------------------------------------------------
# 3. Dependency kiểm tra quyền Admin
# -------------------------------------------------------------------
def get_current_admin(current_user: User = Depends(get_current_user)):
    role_name = current_user.role.value if hasattr(current_user.role, "value") else current_user.role

    if role_name != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Bạn không có quyền Admin"
        )
    return current_user