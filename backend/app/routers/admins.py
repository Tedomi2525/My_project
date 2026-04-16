from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.admin import AdminCreate, AdminResponse, AdminUpdate
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admins", tags=["Admins"])


@router.post("/", response_model=AdminResponse)
def create_admin(admin_in: AdminCreate, db: Session = Depends(get_db)):
    return AdminService.create_admin(db, admin_in)


@router.get("/", response_model=List[AdminResponse])
def get_admins(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return AdminService.get_admins(db, skip, limit)


@router.get("/{admin_id}", response_model=AdminResponse)
def get_admin(admin_id: int, db: Session = Depends(get_db)):
    admin = AdminService.get_admin_by_id(db, admin_id)
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")
    return admin


@router.put("/{admin_id}", response_model=AdminResponse)
def update_admin(admin_id: int, admin_update: AdminUpdate, db: Session = Depends(get_db)):
    admin = AdminService.update_admin(db, admin_id, admin_update)
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")
    return admin


@router.delete("/{admin_id}")
def delete_admin(admin_id: int, db: Session = Depends(get_db)):
    success = AdminService.delete_admin(db, admin_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")
    return {"message": "Admin deleted successfully"}
