from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.class_student import ClassStudent

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

    user = db.query(User).filter(User.id == user_id_int).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User ID không tồn tại hoặc không hợp lệ"
        )
    
    return user

def get_current_teacher(
    current_user: User = Depends(get_current_user)
):
    role = (
        current_user.role.value
        if hasattr(current_user.role, "value")
        else current_user.role
    )

    if role != "teacher":
        raise HTTPException(
            status_code=403,
            detail="Teacher permission required"
        )

    return current_user

def get_current_admin(current_user: User = Depends(get_current_user)):
    role_name = current_user.role.value if hasattr(current_user.role, "value") else current_user.role

    if role_name != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Bạn không có quyền Admin"
        )
    return current_user


def get_current_student(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    role = (
        current_user.role.value
        if hasattr(current_user.role, "value")
        else current_user.role
    )

    if role != "student":
        raise HTTPException(403, "Student permission required")

    class_student = (
        db.query(ClassStudent)
        .filter(ClassStudent.student_id == current_user.id)
        .first()
    )

    if not class_student:
        raise HTTPException(400, "Student has no class")

    # gán tạm class_id cho user (dùng tiếp)
    current_user.class_id = class_student.class_id

    return current_user

