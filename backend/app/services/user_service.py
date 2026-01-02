from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app import models, schemas
from .auth_service import AuthService

class UserService:
    @staticmethod
    def create_user(db: Session, user: schemas.UserCreate):
        # 1. Kiểm tra trùng username
        if db.query(models.User).filter(models.User.username == user.username).first():
            raise HTTPException(status_code=400, detail="Username đã tồn tại")
        
        # 2. Kiểm tra trùng email
        if db.query(models.User).filter(models.User.email == user.email).first():
            raise HTTPException(status_code=400, detail="Email đã tồn tại")

        # 3. Hash mật khẩu
        hashed_pwd = AuthService.get_password_hash(user.password)
        
        # 4. Lưu DB
        db_user = models.User(
            username=user.username,
            password_hash=hashed_pwd,
            full_name=user.full_name,
            email=user.email,
            role=user.role,
            student_code=user.student_code # Map từ studentId của frontend
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user_by_username(db: Session, username: str):
        return db.query(models.User).filter(models.User.username == username).first()