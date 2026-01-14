from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException

from app.models.classroom import Class
from app.models.class_student import ClassStudent
from app.models.user import User
from app.schemas.classroom import ClassCreate


# ---------- MAPPER ----------
def class_to_dict(class_: Class):
    return {
        "id": class_.id,
        "name": class_.name,
        "description": class_.description,
        "teacher_id": class_.teacher_id,
        "student_count": len(class_.students),
        "students": [
            {
                "id": cs.student.id,
                "full_name": cs.student.full_name,
                "email": cs.student.email,
                "joined_at": cs.joined_at
            }
            for cs in class_.students
        ]
    }


class ClassService:

    # ---------- CLASS ----------
    @staticmethod
    def create_class(db: Session, data: ClassCreate, teacher_id: int):
        cls = Class(
            name=data.name,
            description=data.description,
            teacher_id=teacher_id
        )
        db.add(cls)
        db.commit()
        db.refresh(cls)
        return class_to_dict(cls)

    @staticmethod
    def get_class(db: Session, class_id: int):
        cls = db.query(Class).options(
            joinedload(Class.students).joinedload(ClassStudent.student)
        ).filter(Class.id == class_id).first()

        if not cls:
            raise HTTPException(status_code=404, detail="Class not found")

        return class_to_dict(cls)

    @staticmethod
    def get_classes_by_teacher(db: Session, teacher_id: int):
        classes = db.query(Class).filter(
            Class.teacher_id == teacher_id
        ).all()

        return [
            {
                "id": c.id,
                "name": c.name,
                "description": c.description,
                "teacher_id": c.teacher_id,
                "student_count": len(c.students)
            }
            for c in classes
        ]

    @staticmethod
    def update_class(db: Session, class_id: int, data: dict):
        cls = db.query(Class).filter(Class.id == class_id).first()
        if not cls:
            raise HTTPException(status_code=404, detail="Class not found")

        for key, value in data.items():
            setattr(cls, key, value)

        db.commit()
        db.refresh(cls)
        return class_to_dict(cls)

    @staticmethod
    def delete_class(db: Session, class_id: int):
        cls = db.query(Class).filter(Class.id == class_id).first()
        if not cls:
            raise HTTPException(status_code=404, detail="Class not found")

        db.delete(cls)
        db.commit()

    # ---------- STUDENT ----------
    @staticmethod
    def add_student(db: Session, class_id: int, student_id: int):
        student = db.query(User).filter(
            User.id == student_id,
            User.role == "student"
        ).first()

        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        exists = db.query(ClassStudent).filter(
            ClassStudent.class_id == class_id,
            ClassStudent.student_id == student_id
        ).first()

        if exists:
            return

        link = ClassStudent(
            class_id=class_id,
            student_id=student_id
        )
        db.add(link)
        db.commit()

    @staticmethod
    def remove_student(db: Session, class_id: int, student_id: int):
        link = db.query(ClassStudent).filter(
            ClassStudent.class_id == class_id,
            ClassStudent.student_id == student_id
        ).first()

        if not link:
            raise HTTPException(status_code=404, detail="Student not in class")

        db.delete(link)
        db.commit() 

    @staticmethod
    def get_available_students(db: Session, class_id: int):
        subquery = (
            db.query(ClassStudent.student_id)
            .filter(ClassStudent.class_id == class_id)
        )

        students = (
            db.query(User)
            .filter(
                User.role == "student",
                ~User.id.in_(subquery)
            )
            .all()
        )

        return [
            {
                "id": s.id,
                "full_name": s.full_name,
                "email": s.email,
                "student_code": s.student_code
            }
            for s in students
        ]