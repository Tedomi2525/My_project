from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.teacher import TeacherCreate, TeacherResponse, TeacherUpdate
from app.services.teacher_service import TeacherService

router = APIRouter(prefix="/teachers", tags=["Teachers"])


@router.post("/", response_model=TeacherResponse)
def create_teacher(teacher_in: TeacherCreate, db: Session = Depends(get_db)):
    return TeacherService.create_teacher(db, teacher_in)


@router.get("/", response_model=List[TeacherResponse])
def get_teachers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return TeacherService.get_teachers(db, skip, limit)


@router.get("/{teacher_id}", response_model=TeacherResponse)
def get_teacher(teacher_id: int, db: Session = Depends(get_db)):
    teacher = TeacherService.get_teacher_by_id(db, teacher_id)
    if not teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")
    return teacher


@router.put("/{teacher_id}", response_model=TeacherResponse)
def update_teacher(teacher_id: int, teacher_update: TeacherUpdate, db: Session = Depends(get_db)):
    teacher = TeacherService.update_teacher(db, teacher_id, teacher_update)
    if not teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")
    return teacher


@router.delete("/{teacher_id}")
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    success = TeacherService.delete_teacher(db, teacher_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")
    return {"message": "Teacher deleted successfully"}
