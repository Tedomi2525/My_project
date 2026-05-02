from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.jwt import create_access_token
from app.services.account_service import AccountService
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    try:
        return _login(login_data, db)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {type(exc).__name__}: {exc}",
        )


@router.post("/debug-login")
def debug_login(login_data: LoginRequest, db: Session = Depends(get_db)):
    steps = []
    try:
        steps.append("find_account:start")
        account = AccountService.find_by_username(db, login_data.username)
        steps.append(f"find_account:done:{bool(account)}")
        if not account:
            return {"ok": False, "steps": steps, "error": "account not found"}

        steps.append("verify_password:start")
        password_ok = AccountService.verify_password(login_data.password, account.password)
        steps.append(f"verify_password:done:{password_ok}")
        if not password_ok:
            return {"ok": False, "steps": steps, "error": "wrong password"}

        steps.append("create_token:start")
        access_token = create_access_token(
            data={
                "sub": account.username,
                "role": account.role,
                "user_id": account.id,
                "username": account.username,
                "full_name": account.full_name,
                "email": getattr(account, "email", None),
                "student_id": getattr(account, "student_code", None)
            }
        )
        steps.append("create_token:done")

        return {
            "ok": True,
            "steps": steps,
            "user_id": account.id,
            "role": account.role,
            "full_name": account.full_name,
            "email": getattr(account, "email", None),
            "token_prefix": access_token[:20],
        }
    except Exception as exc:
        return {
            "ok": False,
            "steps": steps,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }


def _login(login_data: LoginRequest, db: Session):
    account = AccountService.find_by_username(db, login_data.username)

    if not account or not AccountService.verify_password(login_data.password, account.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai tên đăng nhập hoặc mật khẩu",
        )

    access_token = create_access_token(
        data={
            "sub": account.username,
            "role": account.role,
            "user_id": account.id,
            "username": account.username,
            "full_name": account.full_name,
            "email": getattr(account, "email", None),
            "student_id": getattr(account, "student_code", None)
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": account.id,
        "role": account.role,
        "full_name": account.full_name,
        "email": getattr(account, "email", None),
        "student_id": getattr(account, "student_code", None)
    }
