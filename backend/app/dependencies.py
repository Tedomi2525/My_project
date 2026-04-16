from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from app.core.roles import normalize_role, UserRole
from app.database import get_db
from app.models.admin import Admin
from app.models.teacher import Teacher
from app.models.student import Student
from app.models.class_student import ClassStudent


# -------------------------------------------------------------------
# Dependency lấy account hiện tại từ Header
# -------------------------------------------------------------------
def get_current_user(
    x_user_id: str = Header(..., description="ID của người dùng đang đăng nhập"),
    x_user_role: str = Header(..., description="Role của người dùng đang đăng nhập"),
    db: Session = Depends(get_db)
):
    try:
        user_id_int = int(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Header x-user-id phải là số nguyên"
        )

    role = normalize_role(x_user_role)
    if role == UserRole.admin.value:
        user = db.query(Admin).filter(Admin.id == user_id_int).first()
    elif role == UserRole.teacher.value:
        user = db.query(Teacher).filter(Teacher.id == user_id_int).first()
    elif role == UserRole.student.value:
        user = db.query(Student).filter(Student.id == user_id_int).first()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Header x-user-role không hợp lệ"
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User ID không tồn tại hoặc không hợp lệ"
        )

    return user


def get_current_teacher(
    current_user=Depends(get_current_user)
):
    role = normalize_role(current_user.role)
    if role != UserRole.teacher.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher permission required"
        )
    return current_user


def get_current_admin(current_user=Depends(get_current_user)):
    role_name = normalize_role(current_user.role)
    if role_name != UserRole.admin.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền Admin"
        )
    return current_user


def get_current_student(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    role = normalize_role(current_user.role)
    if role != UserRole.student.value:
        raise HTTPException(403, "Student permission required")

    class_student = (
        db.query(ClassStudent)
        .filter(ClassStudent.student_id == current_user.id)
        .first()
    )

    if not class_student:
        raise HTTPException(400, "Student has no class")

    current_user.class_id = class_student.class_id
    return current_user
