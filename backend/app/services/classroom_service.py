from sqlalchemy.orm import Session
from app.models.classroom import Class
from app.models.class_student import ClassStudent
from app.schemas.classroom import ClassCreate
from app.schemas.class_student import ClassStudentCreate

class ClassService:
    # --- CRUD CLASS ---
    @staticmethod
    def create_class(db: Session, class_in: ClassCreate):
        db_class = Class(**class_in.model_dump())
        db.add(db_class)
        db.commit()
        db.refresh(db_class)
        return db_class

    @staticmethod
    def get_class(db: Session, class_id: int):
        return db.query(Class).filter(Class.id == class_id).first()
        
    @staticmethod
    def get_classes(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Class).offset(skip).limit(limit).all()

    @staticmethod
    def update_class(db: Session, class_id: int, class_data: dict):
        db_class = db.query(Class).filter(Class.id == class_id).first()
        if not db_class:
            return None
        for key, value in class_data.items():
            setattr(db_class, key, value)
        db.commit()
        db.refresh(db_class)
        return db_class

    @staticmethod
    def delete_class(db: Session, class_id: int):
        db_class = db.query(Class).filter(Class.id == class_id).first()
        if db_class:
            db.delete(db_class)
            db.commit()
            return True
        return False

    # --- HỌC SINH VÀO LỚP ---
    @staticmethod
    def add_student(db: Session, link_in: ClassStudentCreate):
        existing = db.query(ClassStudent).filter(
            ClassStudent.class_id == link_in.class_id,
            ClassStudent.student_id == link_in.student_id
        ).first()
        if existing:
            return existing
            
        db_link = ClassStudent(**link_in.model_dump())
        db.add(db_link)
        db.commit()
        db.refresh(db_link)
        return db_link

    @staticmethod
    def remove_student(db: Session, class_id: int, student_id: int):
        db_link = db.query(ClassStudent).filter(
            ClassStudent.class_id == class_id,
            ClassStudent.student_id == student_id
        ).first()
        if db_link:
            db.delete(db_link)
            db.commit()
            return True
        return False