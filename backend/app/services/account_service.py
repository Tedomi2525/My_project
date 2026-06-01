import re
from typing import Optional, Tuple, Type
from sqlalchemy import text
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

        legacy_usernames = db.execute(
            text("SELECT username FROM `user` WHERE username LIKE :pattern"),
            {"pattern": f"{prefix}%"},
        ).fetchall()
        for (username,) in legacy_usernames:
            if not username:
                continue
            match = pattern.match(username)
            if match:
                max_number = max(max_number, int(match.group(1)))

        next_number = max_number + 1
        while True:
            code = f"{prefix}{next_number:0{AccountService.CODE_WIDTH}d}"
            if (
                not AccountService.find_by_username(db, code)
                and not AccountService._exists_in_legacy_user(db, "username", code)
            ):
                return code
            next_number += 1

    @staticmethod
    def sync_legacy_user(
        db: Session,
        *,
        user_id: int,
        username: str,
        email: str | None,
        password: str,
        full_name: str | None,
        role: str,
        student_code: str | None = None,
    ) -> None:
        params = {
            "id": user_id,
            "username": username,
            "email": email,
            "password": password,
            "full_name": full_name,
            "role": role,
            "student_code": student_code,
        }

        db.execute(
            text(
                """
                INSERT INTO `user` (id, username, email, password, full_name, role, student_code)
                VALUES (:id, :username, :email, :password, :full_name, :role, :student_code)
                ON DUPLICATE KEY UPDATE
                    id = VALUES(id),
                    username = VALUES(username),
                    email = VALUES(email),
                    password = VALUES(password),
                    full_name = VALUES(full_name),
                    role = VALUES(role),
                    student_code = VALUES(student_code)
                """
            ),
            params,
        )

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
    def _exists_in_legacy_user(
        db: Session,
        field_name: str,
        value: Optional[str],
        exclude_id: Optional[int] = None,
    ) -> bool:
        if not value:
            return False
        query = f"SELECT id FROM `user` WHERE {field_name} = :value"
        params = {"value": value}
        if exclude_id:
            query += " AND id != :exclude_id"
            params["exclude_id"] = exclude_id
        return db.execute(text(query), params).first() is not None

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

        if AccountService._exists_in_legacy_user(db, "username", username, exclude_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username Ä‘Ã£ tá»“n táº¡i"
            )
        if AccountService._exists_in_legacy_user(db, "email", email, exclude_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email Ä‘Ã£ tá»“n táº¡i"
            )
        if AccountService._exists_in_legacy_user(db, "student_code", student_code, exclude_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MÃ£ sinh viÃªn Ä‘Ã£ tá»“n táº¡i"
            )

    @staticmethod
    def handle_db_error(e: Exception):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi database: {str(e)}"
        )
