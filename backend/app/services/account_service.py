import re
from typing import Optional, Tuple, Type
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
import bcrypt

from app.models.admin import Admin
from app.models.teacher import Teacher
from app.models.student import Student


class AccountService:
    CODE_WIDTH = 6

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )

    @staticmethod
    def get_password_hash(password: str) -> str:
        return bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

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
    def generate_account_code(db: Session, prefix: str) -> str:
        pattern = re.compile(rf"^{re.escape(prefix)}(\d+)$")
        max_number = 0

        for model in (Admin, Teacher, Student):
            usernames = (
                db.query(model.username)
                .filter(model.username.like(f"{prefix}%"))
                .all()
            )
            for (username,) in usernames:
                if not username:
                    continue
                match = pattern.match(username)
                if match:
                    max_number = max(max_number, int(match.group(1)))

        next_number = max_number + 1
        while True:
            code = f"{prefix}{next_number:0{AccountService.CODE_WIDTH}d}"
            if not AccountService.find_by_username(db, code):
                return code
            next_number += 1

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
