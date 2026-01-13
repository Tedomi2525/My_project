from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User

from app.schemas.classroom import (
    ClassCreate,
    ClassUpdate,
    ClassResponse,
    ClassDetailResponse
)
from app.schemas.class_student import ClassStudentCreate
from app.services.classroom_service import ClassService

router = APIRouter(
    prefix="/classes",
    tags=["Classes"]
)


# ---------- ROLE CHECK ----------
def require_teacher(user: User):
    if user.role != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher permission required"
        )
    return user


# ---------- GET /classes ----------
@router.get("/", response_model=List[ClassResponse])
def get_classes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_teacher(current_user)
    return ClassService.get_classes_by_teacher(
        db=db,
        teacher_id=current_user.id
    )


# ---------- POST /classes ----------
@router.post("/", response_model=ClassDetailResponse)
def create_class(
    data: ClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_teacher(current_user)
    return ClassService.create_class(
        db=db,
        data=data,
        teacher_id=current_user.id
    )


# ---------- GET /classes/{id} ----------
@router.get("/{class_id}", response_model=ClassDetailResponse)
def get_class_detail(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_teacher(current_user)
    cls = ClassService.get_class(db, class_id)

    if cls["teacher_id"] != current_user.id:
        raise HTTPException(status_code=403)

    return cls

@router.get("/{class_id}/available-students")
def get_available_students(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_teacher(current_user)

    cls = ClassService.get_class(db, class_id)
    if cls["teacher_id"] != current_user.id:
        raise HTTPException(status_code=403)

    return ClassService.get_available_students(db, class_id)



# ---------- PUT /classes/{id} ----------
@router.put("/{class_id}", response_model=ClassDetailResponse)
def update_class(
    class_id: int,
    data: ClassUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_teacher(current_user)
    cls = ClassService.get_class(db, class_id)

    if cls["teacher_id"] != current_user.id:
        raise HTTPException(status_code=403)

    return ClassService.update_class(
        db=db,
        class_id=class_id,
        data=data.model_dump(exclude_unset=True)
    )


# ---------- DELETE /classes/{id} ----------
@router.delete("/{class_id}")
def delete_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_teacher(current_user)
    cls = ClassService.get_class(db, class_id)

    if cls["teacher_id"] != current_user.id:
        raise HTTPException(status_code=403)

    ClassService.delete_class(db, class_id)
    return {"message": "Class deleted successfully"}


# ---------- POST /classes/{id}/students/{student_id} ----------
@router.post("/{class_id}/students/{student_id}")
def add_student(
    class_id: int,
    student_id: int,
    # data: ClassStudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_teacher(current_user)
    cls = ClassService.get_class(db, class_id)

    if cls["teacher_id"] != current_user.id:
        raise HTTPException(status_code=403)

    ClassService.add_student(
        db=db,
        class_id=class_id,
        student_id=student_id
    )
    return {"message": "Student added"}


# ---------- DELETE /classes/{id}/students/{student_id} ----------
@router.delete("/{class_id}/students/{student_id}")
def remove_student(
    class_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_teacher(current_user)
    cls = ClassService.get_class(db, class_id)

    if cls["teacher_id"] != current_user.id:
        raise HTTPException(status_code=403)

    ClassService.remove_student(
        db=db,
        class_id=class_id,
        student_id=student_id
    )
    return {"message": "Student removed"}
