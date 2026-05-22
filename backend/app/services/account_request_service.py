from fastapi import HTTPException, status
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.models.account_request import AccountRequest
from app.models.student import Student
from app.models.teacher import Teacher
from app.database import engine
from app.schemas.account_request import AccountRequestCreate
from app.schemas.student import StudentCreate
from app.schemas.teacher import TeacherCreate
from app.services.student_service import StudentService
from app.services.teacher_service import TeacherService


class AccountRequestService:
    @staticmethod
    def ensure_email_columns() -> None:
        inspector = inspect(engine)
        if not inspector.has_table(AccountRequest.__tablename__):
            return

        existing_columns = {
            column["name"]
            for column in inspector.get_columns(AccountRequest.__tablename__)
        }
        alter_statements = []
        if "email_status" not in existing_columns:
            alter_statements.append(
                "ALTER TABLE account_request ADD COLUMN email_status VARCHAR(20) NOT NULL DEFAULT 'pending'"
            )
        if "email_error" not in existing_columns:
            alter_statements.append(
                "ALTER TABLE account_request ADD COLUMN email_error TEXT NULL"
            )
        if "email_sent_at" not in existing_columns:
            alter_statements.append(
                "ALTER TABLE account_request ADD COLUMN email_sent_at DATETIME NULL"
            )

        if not alter_statements:
            return

        with engine.begin() as connection:
            for statement in alter_statements:
                connection.execute(text(statement))

    @staticmethod
    def create_request(db: Session, request_in: AccountRequestCreate) -> AccountRequest:
        if request_in.role not in {"teacher", "student"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role must be teacher or student",
            )

        if request_in.email:
            existing = (
                db.query(AccountRequest)
                .filter(
                    AccountRequest.email == request_in.email,
                    AccountRequest.role == request_in.role,
                    AccountRequest.status == "pending",
                )
                .first()
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email này đã có yêu cầu đang chờ duyệt",
                )

        account_request = AccountRequest(
            full_name=request_in.full_name.strip(),
            email=request_in.email,
            role=request_in.role,
            note=request_in.note.strip() if request_in.note else None,
            email_status="pending",
        )
        db.add(account_request)
        db.commit()
        db.refresh(account_request)
        return account_request

    @staticmethod
    def get_requests(db: Session, status_filter: str | None = None):
        query = db.query(AccountRequest).order_by(AccountRequest.created_at.desc())
        if status_filter:
            query = query.filter(AccountRequest.status == status_filter)
        return query.all()

    @staticmethod
    def approve_request(db: Session, request_id: int) -> AccountRequest:
        account_request = db.query(AccountRequest).filter(AccountRequest.id == request_id).first()
        if not account_request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
        if account_request.status != "pending":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request already processed")

        if account_request.role == "teacher":
            created_account = TeacherService.create_teacher(
                db,
                TeacherCreate(full_name=account_request.full_name, email=account_request.email),
            )
            default_password = f"{created_account.username}@"
        else:
            created_account = StudentService.create_student(
                db,
                StudentCreate(full_name=account_request.full_name, email=account_request.email),
            )
            default_password = f"{created_account.username}@"

        account_request.status = "approved"
        account_request.created_account_id = created_account.id
        db.commit()
        db.refresh(account_request)

        return account_request

    @staticmethod
    def reject_request(db: Session, request_id: int) -> AccountRequest:
        account_request = db.query(AccountRequest).filter(AccountRequest.id == request_id).first()
        if not account_request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
        if account_request.status != "pending":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request already processed")

        account_request.status = "rejected"
        db.commit()
        db.refresh(account_request)
        return account_request

    @staticmethod
    def get_public_status(db: Session, request_id: int) -> dict:
        account_request = db.query(AccountRequest).filter(AccountRequest.id == request_id).first()
        if not account_request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")

        if account_request.status == "approved" and account_request.created_account_id:
            account = AccountRequestService._get_created_account(db, account_request)
            if account:
                return {
                    "id": account_request.id,
                    "status": account_request.status,
                    "role": account_request.role,
                    "username": account.username,
                    "password": f"{account.username}@",
                    "message": "Tài khoản đã được tạo. Vui lòng ghi nhớ tài khoản và mật khẩu của bạn.",
                }

        if account_request.status == "rejected":
            message = "Yêu cầu tạo tài khoản đã bị từ chối."
        else:
            message = "Yêu cầu đang chờ admin duyệt."

        return {
            "id": account_request.id,
            "status": account_request.status,
            "role": account_request.role,
            "username": None,
            "password": None,
            "message": message,
        }

    @staticmethod
    def _get_created_account(db: Session, account_request: AccountRequest):
        model = Teacher if account_request.role == "teacher" else Student
        return db.query(model).filter(model.id == account_request.created_account_id).first()
