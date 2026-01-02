from sqlalchemy.orm import Session
from fastapi import HTTPException
from app import models

class ClassroomMemberService:
    @staticmethod
    def add_student_to_class(db: Session, class_id: int, student_id: int):
        # Check lớp
        if not db.query(models.Classroom).filter(models.Classroom.class_id == class_id).first():
            raise HTTPException(status_code=404, detail="Lớp học không tồn tại")
        
        # Check sinh viên
        if not db.query(models.User).filter(models.User.user_id == student_id).first():
            raise HTTPException(status_code=404, detail="Sinh viên không tồn tại")

        # Check đã tồn tại chưa
        exists = db.query(models.ClassroomMember).filter(
            models.ClassroomMember.class_id == class_id,
            models.ClassroomMember.student_id == student_id
        ).first()
        
        if exists:
            raise HTTPException(status_code=400, detail="Sinh viên đã có trong lớp này")

        new_member = models.ClassroomMember(class_id=class_id, student_id=student_id)
        db.add(new_member)
        db.commit()
        return new_member

    @staticmethod
    def remove_student_from_class(db: Session, class_id: int, student_id: int):
        member = db.query(models.ClassroomMember).filter(
            models.ClassroomMember.class_id == class_id,
            models.ClassroomMember.student_id == student_id
        ).first()
        
        if not member:
            raise HTTPException(status_code=404, detail="Sinh viên không có trong lớp này")
            
        db.delete(member)
        db.commit()
        return True