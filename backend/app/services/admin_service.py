from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from app.models.admin import Admin
from app.schemas.admin import AdminCreate, AdminUpdate
from app.services.account_service import AccountService


class AdminService:
    @staticmethod
    def create_admin(db: Session, admin_in: AdminCreate) -> Admin:
        try:
            AccountService.ensure_unique_identity(
                db,
                username=admin_in.username,
                email=admin_in.email
            )
            hashed_password = AccountService.get_password_hash(admin_in.password)

            admin = Admin(
                username=admin_in.username,
                email=admin_in.email,
                password=hashed_password,
                full_name=admin_in.full_name
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            return admin
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            AccountService.handle_db_error(e)

    @staticmethod
    def get_admins(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Admin).offset(skip).limit(limit).all()

    @staticmethod
    def get_admin_by_id(db: Session, admin_id: int):
        return db.query(Admin).filter(Admin.id == admin_id).first()

    @staticmethod
    def update_admin(db: Session, admin_id: int, data: AdminUpdate):
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        if not admin:
            return None

        update_data = data.dict(exclude_unset=True)
        if "password" in update_data and update_data["password"]:
            update_data["password"] = AccountService.get_password_hash(update_data["password"])

        AccountService.ensure_unique_identity(
            db,
            username=update_data.get("username", admin.username),
            email=update_data.get("email", admin.email),
            exclude=(Admin, admin.id)
        )

        for key, value in update_data.items():
            setattr(admin, key, value)

        try:
            db.commit()
            db.refresh(admin)
            return admin
        except SQLAlchemyError as e:
            db.rollback()
            AccountService.handle_db_error(e)

    @staticmethod
    def delete_admin(db: Session, admin_id: int) -> bool:
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        if not admin:
            return False

        try:
            db.delete(admin)
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            AccountService.handle_db_error(e)
