from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=List[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

@router.post("/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check trùng username
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username đã tồn tại")
    
    # Map Schema -> Model
    db_user = models.User(
        username=user.username,
        password_hash=user.password, # Thực tế phải hash password ở đây
        full_name=user.full_name,
        email=user.email,
        role=user.role,
        # Lưu ý: Model dùng student_code, Schema dùng student_id (alias)
        student_code=user.student_code 
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user