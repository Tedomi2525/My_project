from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_admin
from app.schemas.account_request import (
    AccountRequestCreate,
    AccountRequestResponse,
    AccountRequestStatusResponse,
)
from app.services.account_request_service import AccountRequestService

router = APIRouter(prefix="/account-requests", tags=["Account Requests"])


@router.post("/", response_model=AccountRequestResponse)
def create_account_request(
    request_in: AccountRequestCreate,
    db: Session = Depends(get_db),
):
    return AccountRequestService.create_request(db, request_in)


@router.get("/", response_model=List[AccountRequestResponse])
def get_account_requests(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    return AccountRequestService.get_requests(db, status)


@router.get("/{request_id}/status", response_model=AccountRequestStatusResponse)
def get_account_request_status(
    request_id: int,
    db: Session = Depends(get_db),
):
    return AccountRequestService.get_public_status(db, request_id)


@router.post("/{request_id}/approve", response_model=AccountRequestResponse)
def approve_account_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    return AccountRequestService.approve_request(db, request_id)


@router.post("/{request_id}/reject", response_model=AccountRequestResponse)
def reject_account_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    return AccountRequestService.reject_request(db, request_id)
