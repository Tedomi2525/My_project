from sqlalchemy.orm import Session
from app.models.classroom_member import ClassroomMember
from typing import List

class ClassroomMemberService:
    @staticmethod
    def add_students_to_class(db: Session, class_id: int, student_ids: List[int]):
        # Lặp qua danh sách ID sinh viên và thêm vào lớp
        created_records = []
        for student_id in student_ids:
            # Kiểm tra xem đã tồn tại chưa để tránh lỗi Duplicate
            exists = db.query(ClassroomMember).filter_by(class_id=class_id, student_id=student_id).first()
            if not exists:
                new_member = ClassroomMember(class_id=class_id, student_id=student_id)
                db.add(new_member)
                created_records.append(new_member)
        
        db.commit()
        return created_records

    @staticmethod
    def remove_student_from_class(db: Session, class_id: int, student_id: int):
        record = db.query(ClassroomMember).filter_by(class_id=class_id, student_id=student_id).first()
        if record:
            db.delete(record)
            db.commit()
            return True
        return False