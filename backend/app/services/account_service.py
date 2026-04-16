from typing import Optional, Tuple, Type
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from passlib.context import CryptContext

from app.models.admin import Admin
from app.models.teacher import Teacher
from app.models.student import Student

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AccountService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def find_by_username(db: Session, username: str):
        admin = db.query(Admin).filter(Admin.username == username).first()
        if admin:
            return admin
        teacher = db.query(Teacher).filter(Teacher.username == username).first()
        if teacher:
            return teacher
        student = db.query(Student).filter(Student.username == username).first()
        if student:
            return student
        return None

    @staticmethod
    def _exists_in_model(
        db: Session,
        model: Type,
        field,
        value: Optional[str],
        exclude_id: Optional[int] = None
    ) -> bool:
        if not value:
            return False
        q = db.query(model).filter(field == value)
        if exclude_id:
            q = q.filter(model.id != exclude_id)
        return db.query(q.exists()).scalar()

    @staticmethod
    def ensure_unique_identity(
        db: Session,
        username: Optional[str],
        email: Optional[str],
        student_code: Optional[str] = None,
        exclude: Optional[Tuple[Type, int]] = None
    ):
        exclude_model = exclude[0] if exclude else None
        exclude_id = exclude[1] if exclude else None

        for model in (Admin, Teacher, Student):
            model_exclude_id = exclude_id if exclude_model is model else None

            if AccountService._exists_in_model(db, model, model.username, username, model_exclude_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username đã tồn tại"
                )
            if AccountService._exists_in_model(db, model, model.email, email, model_exclude_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email đã tồn tại"
                )
            if model is Student:
                if AccountService._exists_in_model(db, Student, Student.student_code, student_code, model_exclude_id):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Mã sinh viên đã tồn tại"
                    )

    @staticmethod
    def handle_db_error(e: Exception):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi database: {str(e)}"
        )
