from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.account_security import AccountSecurity


class LoginSecurityService:
    MAX_FAILURES = 5
    LOCK_MINUTES = 15

    @staticmethod
    def get(db: Session, account):
        row = (
            db.query(AccountSecurity)
            .filter(
                AccountSecurity.role == account.role,
                AccountSecurity.user_id == account.id,
            )
            .first()
        )
        if not row:
            row = AccountSecurity(role=account.role, user_id=account.id)
            db.add(row)
            db.flush()
        return row

    @staticmethod
    def ensure_login_allowed(db: Session, account):
        row = LoginSecurityService.get(db, account)
        if row.is_locked:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Tài khoản đã bị quản trị viên khóa",
            )
        if row.locked_until and row.locked_until > datetime.utcnow():
            remaining = max(1, int((row.locked_until - datetime.utcnow()).total_seconds() / 60) + 1)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Đăng nhập bị tạm khóa. Vui lòng thử lại sau {remaining} phút",
            )
        if row.locked_until:
            row.locked_until = None
            row.failed_attempts = 0
            db.commit()

    @staticmethod
    def record_failure(db: Session, account):
        row = LoginSecurityService.get(db, account)
        row.failed_attempts = (row.failed_attempts or 0) + 1
        if row.failed_attempts >= LoginSecurityService.MAX_FAILURES:
            row.locked_until = datetime.utcnow() + timedelta(
                minutes=LoginSecurityService.LOCK_MINUTES
            )
        db.commit()

    @staticmethod
    def record_success(db: Session, account):
        row = LoginSecurityService.get(db, account)
        row.failed_attempts = 0
        row.locked_until = None
        db.commit()
