from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.classroom import ClassCreate, ClassResponse
from app.schemas.class_student import ClassStudentCreate, ClassStudentResponse
from app.services.classroom_service import ClassService

router = APIRouter(prefix="/classes", tags=["Classes"])

# --- CRUD LỚP HỌC ---
@router.post("/", response_model=ClassResponse)
def create_class(cls: ClassCreate, db: Session = Depends(get_db)):
    return ClassService.create_class(db, cls)

@router.get("/", response_model=List[ClassResponse])
def get_classes(db: Session = Depends(get_db)):
    return ClassService.get_classes(db)

@router.get("/{class_id}", response_model=ClassResponse)
def get_class(class_id: int, db: Session = Depends(get_db)):
    cls = ClassService.get_class(db, class_id)
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    return cls

@router.put("/{class_id}", response_model=ClassResponse)
def update_class(class_id: int, class_data: dict, db: Session = Depends(get_db)):
    cls = ClassService.update_class(db, class_id, class_data)
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    return cls

@router.delete("/{class_id}")
def delete_class(class_id: int, db: Session = Depends(get_db)):
    success = ClassService.delete_class(db, class_id)
    if not success:
        raise HTTPException(status_code=404, detail="Class not found")
    return {"message": "Class deleted"}

# --- QUẢN LÝ HỌC SINH TRONG LỚP ---
@router.post("/join", response_model=ClassStudentResponse)
def join_class(link: ClassStudentCreate, db: Session = Depends(get_db)):
    return ClassService.add_student(db, link)

@router.delete("/{class_id}/students/{student_id}")
def leave_class(class_id: int, student_id: int, db: Session = Depends(get_db)):
    success = ClassService.remove_student(db, class_id, student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found in this class")
    return {"message": "Student removed from class"}