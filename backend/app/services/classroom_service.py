from sqlalchemy.orm import Session
from app.models.classroom import Classroom
from app.schemas.classroom import ClassroomCreate

class ClassroomService:
    @staticmethod
    def create_classroom(db: Session, classroom: ClassroomCreate, teacher_id: int):
        db_class = Classroom(
            class_name=classroom.class_name,
            teacher_id=teacher_id
        )
        db.add(db_class)
        db.commit()
        db.refresh(db_class)
        return db_class

    @staticmethod
    def get_classes_by_teacher(db: Session, teacher_id: int):
        return db.query(Classroom).filter(Classroom.teacher_id == teacher_id).all()
        
    @staticmethod
    def get_class_by_id(db: Session, class_id: int):
        return db.query(Classroom).filter(Classroom.class_id == class_id).first()