from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.roles import normalize_role, UserRole
from app.database import get_db
from app.dependencies import get_current_user

from app.schemas.classroom import (
    ClassCreate,
    ClassUpdate,
    ClassResponse,
    ClassDetailResponse
)
from app.services.classroom_service import ClassService

router = APIRouter(
    prefix="/classes",
    tags=["Classes"]
)


def get_current_teacher(user=Depends(get_current_user)):
    if normalize_role(user.role) != UserRole.teacher.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher permission required"
        )
    return user


@router.get("/", response_model=List[ClassResponse])
def get_classes(
    db: Session = Depends(get_db),
    current_teacher=Depends(get_current_teacher)
):
    return ClassService.get_classes_by_teacher(
        db=db,
        teacher_id=current_teacher.id
    )


@router.post("/", response_model=ClassDetailResponse)
def create_class(
    data: ClassCreate,
    db: Session = Depends(get_db),
    current_teacher=Depends(get_current_teacher)
):
    return ClassService.create_class(
        db=db,
        data=data,
        teacher_id=current_teacher.id
    )


@router.get("/{class_id}", response_model=ClassDetailResponse)
def get_class_detail(
    class_id: int,
    db: Session = Depends(get_db),
    current_teacher=Depends(get_current_teacher)
):
    cls = ClassService.get_class(db, class_id)

    if cls["teacher_id"] != current_teacher.id:
        raise HTTPException(status_code=403, detail="Not your class")

    return cls


@router.get("/{class_id}/available-students")
def get_available_students(
    class_id: int,
    db: Session = Depends(get_db),
    current_teacher=Depends(get_current_teacher)
):
    cls = ClassService.get_class(db, class_id)
    if cls["teacher_id"] != current_teacher.id:
        raise HTTPException(status_code=403, detail="Not your class")

    return ClassService.get_available_students(db, class_id)


@router.put("/{class_id}", response_model=ClassDetailResponse)
def update_class(
    class_id: int,
    data: ClassUpdate,
    db: Session = Depends(get_db),
    current_teacher=Depends(get_current_teacher)
):
    cls = ClassService.get_class(db, class_id)

    if cls["teacher_id"] != current_teacher.id:
        raise HTTPException(status_code=403, detail="Not your class")

    return ClassService.update_class(
        db=db,
        class_id=class_id,
        data=data.model_dump(exclude_unset=True)
    )


@router.delete("/{class_id}")
def delete_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_teacher=Depends(get_current_teacher)
):
    cls = ClassService.get_class(db, class_id)

    if cls["teacher_id"] != current_teacher.id:
        raise HTTPException(status_code=403, detail="Not your class")

    ClassService.delete_class(db, class_id)
    return {"message": "Class deleted successfully"}


@router.post("/{class_id}/students/{student_id}")
def add_student(
    class_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_teacher=Depends(get_current_teacher)
):
    cls = ClassService.get_class(db, class_id)

    if cls["teacher_id"] != current_teacher.id:
        raise HTTPException(status_code=403, detail="Not your class")

    ClassService.add_student(
        db=db,
        class_id=class_id,
        student_id=student_id
    )
    return {"message": "Student added"}


@router.delete("/{class_id}/students/{student_id}")
def remove_student(
    class_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_teacher=Depends(get_current_teacher)
):
    cls = ClassService.get_class(db, class_id)

    if cls["teacher_id"] != current_teacher.id:
        raise HTTPException(status_code=403, detail="Not your class")

    ClassService.remove_student(
        db=db,
        class_id=class_id,
        student_id=student_id
    )
    return {"message": "Student removed"}
