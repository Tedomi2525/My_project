from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.exam_result import ExamResult
from app.models.exam_student_policy import ExamStudentPolicy


class ExamPolicyService:
    @staticmethod
    def get(db: Session, exam_id: int, student_id: int):
        return db.query(ExamStudentPolicy).filter(
            ExamStudentPolicy.exam_id == exam_id,
            ExamStudentPolicy.student_id == student_id,
        ).first()

    @staticmethod
    def ensure_active(db: Session, exam_id: int, student_id: int):
        policy = ExamPolicyService.get(db, exam_id, student_id)
        if policy and policy.session_state == "paused":
            raise HTTPException(status_code=423, detail="Phiên thi đang được giảng viên tạm dừng")
        if policy and policy.session_state == "cancelled":
            raise HTTPException(status_code=403, detail="Phiên thi đã bị giảng viên hủy")
        return policy

    @staticmethod
    def allowed_attempts(db: Session, exam, student_id: int):
        if exam.max_attempts is None:
            return None
        policy = ExamPolicyService.get(db, exam.id, student_id)
        return exam.max_attempts + (policy.extra_attempts if policy else 0)

    @staticmethod
    def effective_end_time(exam, policy):
        if not exam.end_time:
            return None
        extra_minutes = policy.extra_minutes if policy else 0
        paused_seconds = policy.total_paused_seconds if policy else 0
        return exam.end_time.replace(tzinfo=None) + timedelta(
            minutes=extra_minutes,
            seconds=paused_seconds,
        )