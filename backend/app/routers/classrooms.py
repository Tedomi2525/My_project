from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/classes", tags=["Classrooms"])

# 1. Lấy danh sách lớp học
@router.get("/", response_model=List[schemas.ClassroomResponse])
def get_classes(db: Session = Depends(get_db)):
    # Lấy tất cả lớp học
    classes = db.query(models.Classroom).all()
    
    # Logic tính toán trường 'student_count' mà Database không có sẵn
    # SQLAlchemy relationship 'members' sẽ giúp lấy danh sách sinh viên
    for cls in classes:
        cls.student_count = len(cls.members)
        
    return classes

# 2. Tạo lớp học mới
@router.post("/", response_model=schemas.ClassroomResponse)
def create_class(cls_in: schemas.ClassroomCreate, db: Session = Depends(get_db)):
    db_class = models.Classroom(
        class_name=cls_in.class_name,
        teacher_id=1  # Hardcode ID giáo viên (thực tế lấy từ Token)
    )
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    
    # Gán giá trị mặc định để trả về khớp Schema
    db_class.student_count = 0
    return db_class

# 3. Xóa lớp học
@router.delete("/{class_id}")
def delete_class(class_id: int, db: Session = Depends(get_db)):
    db_class = db.query(models.Classroom).filter(models.Classroom.class_id == class_id).first()
    if not db_class:
        raise HTTPException(status_code=404, detail="Lớp học không tồn tại")
    
    db.delete(db_class)
    db.commit()
    return {"message": "Đã xóa lớp học"}

# --- QUẢN LÝ SINH VIÊN TRONG LỚP ---

# 4. Thêm sinh viên vào lớp
@router.post("/{class_id}/students/{student_id}")
def add_student_to_class(class_id: int, student_id: int, db: Session = Depends(get_db)):
    # Kiểm tra lớp tồn tại
    cls = db.query(models.Classroom).filter(models.Classroom.class_id == class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Lớp học không tồn tại")

    # Kiểm tra sinh viên tồn tại
    student = db.query(models.User).filter(models.User.user_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Sinh viên không tồn tại")

    # Kiểm tra xem đã tham gia chưa
    exists = db.query(models.ClassroomMember).filter(
        models.ClassroomMember.class_id == class_id,
        models.ClassroomMember.student_id == student_id
    ).first()
    
    if exists:
        raise HTTPException(status_code=400, detail="Sinh viên này đã có trong lớp")

    # Thêm vào bảng trung gian
    new_member = models.ClassroomMember(class_id=class_id, student_id=student_id)
    db.add(new_member)
    db.commit()
    
    return {"message": "Thêm sinh viên thành công"}

# 5. Xóa sinh viên khỏi lớp
@router.delete("/{class_id}/students/{student_id}")
def remove_student_from_class(class_id: int, student_id: int, db: Session = Depends(get_db)):
    member = db.query(models.ClassroomMember).filter(
        models.ClassroomMember.class_id == class_id,
        models.ClassroomMember.student_id == student_id
    ).first()
    
    if not member:
        raise HTTPException(status_code=404, detail="Sinh viên không có trong lớp này")
        
    db.delete(member)
    db.commit()
    
    return {"message": "Đã xóa sinh viên khỏi lớp"}