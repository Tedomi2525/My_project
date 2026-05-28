from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.database import SessionLocal  # noqa: E402
from app.models.student import Student  # noqa: E402
from app.models.teacher import Teacher  # noqa: E402
from app.services.account_service import AccountService  # noqa: E402


def main() -> None:
    db = SessionLocal()
    try:
        teachers = db.query(Teacher).all()
        students = db.query(Student).all()

        for teacher in teachers:
            AccountService.sync_legacy_user(
                db,
                user_id=teacher.id,
                username=teacher.username,
                email=teacher.email,
                password=teacher.password,
                full_name=teacher.full_name,
                role="teacher",
            )

        for student in students:
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
        print(f"Synced teachers to legacy user table: {len(teachers)}")
        print(f"Synced students to legacy user table: {len(students)}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
