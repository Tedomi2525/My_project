from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from app.models.teacher import Teacher
from app.schemas.teacher import TeacherCreate, TeacherUpdate
from app.services.account_service import AccountService


class TeacherService:
    @staticmethod
    def create_teacher(db: Session, teacher_in: TeacherCreate) -> Teacher:
        try:
            AccountService.ensure_unique_identity(
                db,
                username=teacher_in.username,
                email=teacher_in.email
            )
            hashed_password = AccountService.get_password_hash(teacher_in.password)

            teacher = Teacher(
                username=teacher_in.username,
                email=teacher_in.email,
                password=hashed_password,
                full_name=teacher_in.full_name
            )
            db.add(teacher)
            db.commit()
            db.refresh(teacher)
            return teacher
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            AccountService.handle_db_error(e)

    @staticmethod
    def get_teachers(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Teacher).offset(skip).limit(limit).all()

    @staticmethod
    def get_teacher_by_id(db: Session, teacher_id: int):
        return db.query(Teacher).filter(Teacher.id == teacher_id).first()

    @staticmethod
    def update_teacher(db: Session, teacher_id: int, data: TeacherUpdate):
        teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
        if not teacher:
            return None

        update_data = data.dict(exclude_unset=True)
        if "password" in update_data and update_data["password"]:
            update_data["password"] = AccountService.get_password_hash(update_data["password"])

        AccountService.ensure_unique_identity(
            db,
            username=update_data.get("username", teacher.username),
            email=update_data.get("email", teacher.email),
            exclude=(Teacher, teacher.id)
        )

        for key, value in update_data.items():
            setattr(teacher, key, value)

        try:
            db.commit()
            db.refresh(teacher)
            return teacher
        except SQLAlchemyError as e:
            db.rollback()
            AccountService.handle_db_error(e)

    @staticmethod
    def delete_teacher(db: Session, teacher_id: int) -> bool:
        teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
        if not teacher:
            return False

        try:
            db.delete(teacher)
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            AccountService.handle_db_error(e)
