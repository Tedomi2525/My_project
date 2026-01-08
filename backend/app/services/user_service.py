from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status
from passlib.context import CryptContext

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    # ---------------- CREATE USER ----------------
    @staticmethod
    def create_user(db: Session, user_in: UserCreate) -> User:
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

        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username hoặc email đã tồn tại"
            )
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi database: {str(e)}"
            )

    # ---------------- GET USERS ----------------
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100):
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str):
        return db.query(User).filter(User.username == username).first()

    # ---------------- UPDATE USER ----------------
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        update_data = user_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            if key == "password" and value:
                value = UserService.get_password_hash(value)
            setattr(user, key, value)

        try:
            db.commit()
            db.refresh(user)
            return user
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi cập nhật user: {str(e)}"
            )

    # ---------------- DELETE USER ----------------
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        try:
            db.delete(user)
            db.commit()
            return True
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User đang có dữ liệu liên quan, không thể xóa"
            )
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi database: {str(e)}"
            )
