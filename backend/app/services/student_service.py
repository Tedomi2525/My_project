from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate
from app.services.account_service import AccountService


class StudentService:
    @staticmethod
    def create_student(db: Session, student_in: StudentCreate) -> Student:
        try:
            AccountService.ensure_unique_identity(
                db,
                username=student_in.username,
                email=student_in.email,
                student_code=student_in.student_id
            )
            hashed_password = AccountService.get_password_hash(student_in.password)

            student = Student(
                username=student_in.username,
                email=student_in.email,
                password=hashed_password,
                full_name=student_in.full_name,
                student_code=student_in.student_id
            )
            db.add(student)
            db.commit()
            db.refresh(student)
            return student
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            AccountService.handle_db_error(e)

    @staticmethod
    def get_students(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Student).offset(skip).limit(limit).all()

    @staticmethod
    def get_student_by_id(db: Session, student_id: int):
        return db.query(Student).filter(Student.id == student_id).first()

    @staticmethod
    def update_student(db: Session, student_id: int, data: StudentUpdate):
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return None

        update_data = data.dict(exclude_unset=True)
        if "password" in update_data and update_data["password"]:
            update_data["password"] = AccountService.get_password_hash(update_data["password"])
        if "student_id" in update_data:
            update_data["student_code"] = update_data.pop("student_id")

        AccountService.ensure_unique_identity(
            db,
            username=update_data.get("username", student.username),
            email=update_data.get("email", student.email),
            student_code=update_data.get("student_code", student.student_code),
            exclude=(Student, student.id)
        )

        for key, value in update_data.items():
            setattr(student, key, value)

        try:
            db.commit()
            db.refresh(student)
            return student
        except SQLAlchemyError as e:
            db.rollback()
            AccountService.handle_db_error(e)

    @staticmethod
    def delete_student(db: Session, student_id: int) -> bool:
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return False

        try:
            db.delete(student)
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            AccountService.handle_db_error(e)
