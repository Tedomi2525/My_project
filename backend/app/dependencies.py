from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import ALGORITHM, SECRET_KEY
from app.core.roles import UserRole, normalize_role
from app.database import get_db
from app.models.admin import Admin
from app.models.class_student import ClassStudent
from app.models.student import Student
from app.models.teacher import Teacher


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        role = normalize_role(payload.get("role"))
        if user_id is None or not role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_id_int = int(user_id)
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if role == UserRole.admin.value:
        user = db.query(Admin).filter(Admin.id == user_id_int).first()
    elif role == UserRole.teacher.value:
        user = db.query(Teacher).filter(Teacher.id == user_id_int).first()
    elif role == UserRole.student.value:
        user = db.query(Student).filter(Student.id == user_id_int).first()
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token role",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token user does not exist",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_teacher(current_user=Depends(get_current_user)):
    role = normalize_role(current_user.role)
    if role != UserRole.teacher.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher permission required",
        )
    return current_user


def get_current_admin(current_user=Depends(get_current_user)):
    role_name = normalize_role(current_user.role)
    if role_name != UserRole.admin.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permission required",
        )
    return current_user


def get_current_student(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    role = normalize_role(current_user.role)
    if role != UserRole.student.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student permission required",
        )

    class_ids = [
        row[0]
        for row in (
            db.query(ClassStudent.class_id)
            .filter(ClassStudent.student_id == current_user.id)
            .all()
        )
    ]

    if not class_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student has no class",
        )

    current_user.class_ids = class_ids
    current_user.class_id = class_ids[0]
    return current_user
