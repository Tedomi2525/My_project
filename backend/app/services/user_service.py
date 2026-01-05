from sqlalchemy.orm import Session
from passlib.context import CryptContext

# Nhớ là phải có app.
from app.models.user import User
from app.schemas.user import UserCreate

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:  # <--- Kiểm tra kỹ tên class này
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)
    # ------------------------

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)

    @staticmethod
    def create_user(db: Session, user_in: UserCreate):
        try:
            hashed_password = UserService.get_password_hash(user_in.password)

            db_user = User(
                username=user_in.username,
                email=user_in.email,
                password=hashed_password,
                full_name=user_in.full_name,
                role=user_in.role
            )

            db.add(db_user)
            db.commit()
            db.refresh(db_user)

            return db_user

        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi database: {str(e)}"
            )

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Lỗi tạo user: {str(e)}"
            )

    @staticmethod
    def get_user_by_username(db: Session, username: str):
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str):
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100):
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def update_user(db: Session, user_id: int, user_data: dict):
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            for key, value in user_data.items():
                if key == 'password':
                    value = UserService.get_password_hash(value)
                setattr(user, key, value)
            db.commit()
            db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        return False