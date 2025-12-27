from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.schemas.classroom import ClassroomCreate, ClassroomResponse
from app.schemas.classroom_member import AddStudentToClass
from app.services import ClassroomService, ClassroomMemberService
from app.dependencies import get_current_teacher, get_current_user

router = APIRouter(prefix="/classes", tags=["Classrooms"])

@router.post("/", response_model=ClassroomResponse)
def create_class(
    classroom: ClassroomCreate, 
    db: Session = Depends(get_db), 
    teacher: User = Depends(get_current_teacher)
):
    return ClassroomService.create_classroom(db, classroom, teacher_id=teacher.user_id)

@router.get("/", response_model=List[ClassroomResponse])
def get_my_classes(
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    # Nếu là Teacher -> Trả về lớp mình dạy
    if user.role == "Teacher":
        return ClassroomService.get_classes_by_teacher(db, user.user_id)
    # Nếu là Student -> Trả về lớp mình học (Logic này cần viết thêm trong Service nếu cần)
    return [] 

@router.post("/{class_id}/students")
def add_students(
    class_id: int, 
    data: AddStudentToClass, 
    db: Session = Depends(get_db),
    teacher: User = Depends(get_current_teacher)
):
    # Check quyền: User hiện tại có phải chủ nhiệm lớp này không (Bỏ qua để demo cho nhanh)
    return ClassroomMemberService.add_students_to_class(db, class_id, data.student_ids)
from app.schemas.classroom import ClassroomUpdate

@router.put("/{class_id}", response_model=ClassroomResponse)
def update_class(
    class_id: int, 
    data: ClassroomUpdate, 
    db: Session = Depends(get_db),
    teacher: User = Depends(get_current_teacher)
):
    updated = ClassroomService.update_classroom(db, class_id, data.class_name, teacher.user_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Lớp không tồn tại hoặc không có quyền")
    return updated

@router.delete("/{class_id}", status_code=204)
def delete_class(
    class_id: int, 
    db: Session = Depends(get_db),
    teacher: User = Depends(get_current_teacher)
):
    success = ClassroomService.delete_classroom(db, class_id, teacher.user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Lỗi khi xóa lớp")
    return None
@router.delete("/{class_id}/students/{student_id}", status_code=204)
def remove_student(
    class_id: int, 
    student_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(get_current_teacher)
):
    # Logic xóa nằm ở ClassroomMemberService (đã viết ở các bước trước)
    success = ClassroomMemberService.remove_student_from_class(db, class_id, student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sinh viên không có trong lớp này")
    return None