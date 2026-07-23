from sqlalchemy.orm import Session

from app.models.student import Student
from app.services.account_service import AccountService


def create_imported_student(
    db: Session,
    full_name: str,
    email=None,
    student_code=None,
) -> Student:
    code = (
        str(student_code).strip()
        if student_code
        else AccountService.generate_account_code(db, "SV")
    )
    address = str(email).strip().lower() if email else f"{code}@edu.com"
    AccountService.ensure_unique_identity(
        db, username=code, email=address, student_code=code
    )
    student = Student(
        username=code,
        email=address,
        password=AccountService.get_password_hash(f"{code}@"),
        full_name=full_name,
        student_code=code,
    )
    db.add(student)
    db.flush()
    AccountService.sync_legacy_user(
        db,
        user_id=student.id,
        username=student.username,
        email=student.email,
        password=student.password,
        full_name=student.full_name,
        role="student",
        student_code=student.student_code,
    )
    db.commit()
    db.refresh(student)
    return student
