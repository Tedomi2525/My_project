import hashlib
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_admin, get_current_user
from app.models.account_security import AccountSecurity
from app.models.admin import Admin
from app.models.audit_log import AuditLog
from app.models.password_reset_token import PasswordResetToken
from app.models.student import Student
from app.models.teacher import Teacher
from app.services.account_service import AccountService
from app.services.audit_service import AuditService
from app.services.password_email_service import send_password_reset_email

router = APIRouter(tags=["Security"])
ACCOUNT_MODELS = {"admin": Admin, "teacher": Teacher, "student": Student}


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=20)
    new_password: str = Field(min_length=8, max_length=72)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=72)


class LockRequest(BaseModel):
    locked: bool


def _find_by_email(db: Session, email: str):
    normalized = email.strip().lower()
    for model in ACCOUNT_MODELS.values():
        account = db.query(model).filter(model.email == normalized).first()
        if account:
            return account
    return None


def _security(db: Session, account, create=True):
    row = (
        db.query(AccountSecurity)
        .filter(
            AccountSecurity.role == account.role,
            AccountSecurity.user_id == account.id,
        )
        .first()
    )
    if not row and create:
        row = AccountSecurity(role=account.role, user_id=account.id)
        db.add(row)
        db.flush()
    return row


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    account = _find_by_email(db, data.email)
    if account:
        raw_token = secrets.token_urlsafe(32)
        db.query(PasswordResetToken).filter(
            PasswordResetToken.role == account.role,
            PasswordResetToken.user_id == account.id,
            PasswordResetToken.used.is_(False),
        ).update({"used": True})
        db.add(
            PasswordResetToken(
                role=account.role,
                user_id=account.id,
                token_hash=hashlib.sha256(raw_token.encode()).hexdigest(),
                expires_at=datetime.utcnow() + timedelta(minutes=30),
            )
        )
        db.commit()
        send_password_reset_email(account.email, account.full_name, raw_token)
    return {"message": "Nếu email tồn tại, hướng dẫn đặt lại mật khẩu đã được gửi."}


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_hash = hashlib.sha256(data.token.encode()).hexdigest()
    token = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used.is_(False),
            PasswordResetToken.expires_at > datetime.utcnow(),
        )
        .first()
    )
    if not token:
        raise HTTPException(status_code=400, detail="Token không hợp lệ hoặc đã hết hạn")
    account = db.query(ACCOUNT_MODELS[token.role]).filter(
        ACCOUNT_MODELS[token.role].id == token.user_id
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Tài khoản không còn tồn tại")
    account.password = AccountService.get_password_hash(data.new_password)
    token.used = True
    security_row = _security(db, account)
    security_row.failed_attempts = 0
    security_row.locked_until = None
    security_row.password_changed_at = datetime.utcnow()
    AccountService.sync_legacy_user(
        db,
        user_id=account.id,
        username=account.username,
        email=account.email,
        password=account.password,
        full_name=account.full_name,
        role=account.role,
        student_code=getattr(account, "student_code", None),
    )
    db.commit()
    return {"message": "Đặt lại mật khẩu thành công"}


@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not AccountService.verify_password(data.current_password, current_user.password):
        raise HTTPException(status_code=400, detail="Mật khẩu hiện tại không đúng")
    if AccountService.verify_password(data.new_password, current_user.password):
        raise HTTPException(status_code=400, detail="Mật khẩu mới phải khác mật khẩu hiện tại")
    current_user.password = AccountService.get_password_hash(data.new_password)
    security_row = _security(db, current_user)
    security_row.password_changed_at = datetime.utcnow()
    AccountService.sync_legacy_user(
        db,
        user_id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        password=current_user.password,
        full_name=current_user.full_name,
        role=current_user.role,
        student_code=getattr(current_user, "student_code", None),
    )
    AuditService.log(db, current_user, "change_password", "account", current_user.id)
    return {"message": "Đổi mật khẩu thành công"}


@router.patch("/admin/accounts/{role}/{user_id}/lock")
def set_account_lock(
    role: str,
    user_id: int,
    data: LockRequest,
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    model = ACCOUNT_MODELS.get(role)
    if not model:
        raise HTTPException(status_code=400, detail="Vai trò không hợp lệ")
    account = db.query(model).filter(model.id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")
    row = _security(db, account)
    row.is_locked = data.locked
    if not data.locked:
        row.failed_attempts = 0
        row.locked_until = None
    db.commit()
    AuditService.log(
        db, admin, "lock_account" if data.locked else "unlock_account",
        "account", user_id, {"role": role},
    )
    return {"locked": row.is_locked}


@router.get("/admin/audit-logs")
def get_audit_logs(
    limit: int = 200,
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(min(max(limit, 1), 1000))
        .all()
    )
