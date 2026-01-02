from sqlalchemy.orm import Session
from fastapi import HTTPException
from app import models, schemas

class ClassroomService:
    @staticmethod
    def get_all_classes(db: Session):
        classes = db.query(models.Classroom).all()
        # Tính toán student_count cho từng lớp
        for cls in classes:
            cls.student_count = len(cls.members)
        return classes

    @staticmethod
    def create_class(db: Session, cls_in: schemas.ClassroomCreate, teacher_id: int):
        db_class = models.Classroom(
            class_name=cls_in.class_name,
            teacher_id=teacher_id
        )
        db.add(db_class)
        db.commit()
        db.refresh(db_class)
        db_class.student_count = 0 # Gán mặc định để trả về
        return db_class

    @staticmethod
    def delete_class(db: Session, class_id: int):
        db_class = db.query(models.Classroom).filter(models.Classroom.class_id == class_id).first()
        if not db_class:
            raise HTTPException(status_code=404, detail="Lớp học không tồn tại")
        
        db.delete(db_class)
        db.commit()
        return True