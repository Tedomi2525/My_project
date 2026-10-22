from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_student, get_current_teacher
from app.models.class_student import ClassStudent
from app.models.classroom import Class
from app.models.exam import Exam
from app.models.exam_allowed_class import ExamAllowedClass
from app.models.exam_result import ExamResult
from app.models.exam_session import ExamSession
from app.models.exam_student_policy import ExamStudentPolicy
from app.models.notification import Notification
from app.models.student import Student

router = APIRouter(tags=["Learning features"])


class PolicyUpdate(BaseModel):
    extra_minutes: int = Field(default=0, ge=0, le=1440)
    extra_attempts: int = Field(default=0, ge=0, le=20)


class SessionAction(BaseModel):
    action: str


def _teacher_exam(db: Session, exam_id: int, teacher_id: int):
    exam = db.query(Exam).filter(Exam.id == exam_id, Exam.created_by == teacher_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Không tìm thấy đề thi")
    return exam


def _policy(db: Session, exam_id: int, student_id: int, create=False):
    item = db.query(ExamStudentPolicy).filter(
        ExamStudentPolicy.exam_id == exam_id,
        ExamStudentPolicy.student_id == student_id,
    ).first()
    if not item and create:
        item = ExamStudentPolicy(exam_id=exam_id, student_id=student_id)
        db.add(item)
        db.flush()
    return item


def _student_exam_ids(db: Session, student_id: int):
    return [row[0] for row in (
        db.query(ExamAllowedClass.exam_id)
        .join(ClassStudent, ClassStudent.class_id == ExamAllowedClass.class_id)
        .filter(ClassStudent.student_id == student_id)
        .distinct().all()
    )]


def _upsert_notification(db: Session, **values):
    item = db.query(Notification).filter(
        Notification.student_id == values["student_id"],
        Notification.notification_key == values["notification_key"],
    ).first()
    if not item:
        item = Notification(**values)
        db.add(item)
    return item


@router.get("/notifications")
def notifications(student=Depends(get_current_student), db: Session = Depends(get_db)):
    exam_ids = _student_exam_ids(db, student.id)
    now = datetime.now()
    exams = db.query(Exam).filter(Exam.id.in_(exam_ids), Exam.status == "published").all() if exam_ids else []
    for exam in exams:
        _upsert_notification(
            db, student_id=student.id, notification_key=f"exam-new-{exam.id}",
            notification_type="new_exam", title="Có đề thi mới",
            message=exam.title, entity_type="exam", entity_id=exam.id,
        )
        if exam.end_time:
            remaining = exam.end_time.replace(tzinfo=None) - now
            if timedelta(0) < remaining <= timedelta(hours=24):
                hours = max(1, int(remaining.total_seconds() / 3600))
                _upsert_notification(
                    db, student_id=student.id, notification_key=f"exam-due-{exam.id}",
                    notification_type="due_soon", title="Bài thi sắp hết hạn",
                    message=f"{exam.title} còn khoảng {hours} giờ", entity_type="exam", entity_id=exam.id,
                )
    results = db.query(ExamResult).filter(ExamResult.student_id == student.id).all()
    exam_map = {exam.id: exam for exam in db.query(Exam).filter(Exam.id.in_([r.exam_id for r in results])).all()} if results else {}
    for result in results:
        _upsert_notification(
            db, student_id=student.id, notification_key=f"result-{result.id}",
            notification_type="result", title="Đã có kết quả",
            message=f"{exam_map.get(result.exam_id).title if result.exam_id in exam_map else 'Bài thi'}: {result.total_score:.2f} điểm",
            entity_type="result", entity_id=result.id,
        )
    db.commit()
    return db.query(Notification).filter(Notification.student_id == student.id).order_by(Notification.created_at.desc()).limit(100).all()


@router.patch("/notifications/{notification_id:int}/read")
def read_notification(notification_id: int, student=Depends(get_current_student), db: Session = Depends(get_db)):
    item = db.query(Notification).filter(Notification.id == notification_id, Notification.student_id == student.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông báo")
    item.is_read = True
    db.commit()
    return {"ok": True}


@router.patch("/notifications/read-all")
def read_all_notifications(student=Depends(get_current_student), db: Session = Depends(get_db)):
    db.query(Notification).filter(Notification.student_id == student.id).update({"is_read": True})
    db.commit()
    return {"ok": True}


@router.get("/calendar/my-exams")
def student_calendar(student=Depends(get_current_student), db: Session = Depends(get_db)):
    exam_ids = _student_exam_ids(db, student.id)
    exams = db.query(Exam).filter(Exam.id.in_(exam_ids), Exam.status == "published").order_by(Exam.start_time).all() if exam_ids else []
    return [{
        "id": exam.id, "title": exam.title, "start_time": exam.start_time,
        "end_time": exam.end_time, "duration_minutes": exam.duration_minutes,
        "status": exam.status,
    } for exam in exams]


@router.get("/exams/{exam_id}/student-policies")
def list_policies(exam_id: int, teacher=Depends(get_current_teacher), db: Session = Depends(get_db)):
    _teacher_exam(db, exam_id, teacher.id)
    students = db.query(Student).join(
        ClassStudent, ClassStudent.student_id == Student.id
    ).join(
        ExamAllowedClass, ExamAllowedClass.class_id == ClassStudent.class_id
    ).filter(ExamAllowedClass.exam_id == exam_id).distinct().all()
    policies = {
        p.student_id: p for p in db.query(ExamStudentPolicy).filter(ExamStudentPolicy.exam_id == exam_id).all()
    }
    return [{
        "student_id": student.id, "student_name": student.full_name,
        "student_code": student.student_code,
        "extra_minutes": policies.get(student.id).extra_minutes if student.id in policies else 0,
        "extra_attempts": policies.get(student.id).extra_attempts if student.id in policies else 0,
        "session_state": policies.get(student.id).session_state if student.id in policies else "active",
    } for student in students]


@router.put("/exams/{exam_id}/students/{student_id}/policy")
def update_policy(exam_id: int, student_id: int, data: PolicyUpdate, teacher=Depends(get_current_teacher), db: Session = Depends(get_db)):
    _teacher_exam(db, exam_id, teacher.id)
    item = _policy(db, exam_id, student_id, create=True)
    item.extra_minutes = data.extra_minutes
    item.extra_attempts = data.extra_attempts
    db.commit()
    db.refresh(item)
    return item


@router.post("/exams/{exam_id}/students/{student_id}/session-action")
def session_action(exam_id: int, student_id: int, data: SessionAction, teacher=Depends(get_current_teacher), db: Session = Depends(get_db)):
    _teacher_exam(db, exam_id, teacher.id)
    action = data.action.strip().lower()
    if action not in {"pause", "resume", "cancel", "allow_retry"}:
        raise HTTPException(status_code=400, detail="Thao tác không hợp lệ")
    item = _policy(db, exam_id, student_id, create=True)
    now = datetime.now()
    if action == "pause" and item.session_state != "paused":
        item.session_state, item.pause_started_at = "paused", now
    elif action == "resume":
        if item.pause_started_at:
            item.total_paused_seconds += int((now - item.pause_started_at).total_seconds())
        item.session_state, item.pause_started_at = "active", None
    elif action == "cancel":
        item.session_state = "cancelled"
        session = db.query(ExamSession).filter(
            ExamSession.exam_id == exam_id, ExamSession.student_id == student_id,
            ExamSession.submitted_at.is_(None),
        ).order_by(ExamSession.id.desc()).first()
        if session:
            session.submitted_at = now
    elif action == "allow_retry":
        item.extra_attempts += 1
        item.session_state, item.pause_started_at = "active", None
    db.commit()
    return {"state": item.session_state, "extra_attempts": item.extra_attempts}


@router.get("/exams/{exam_id}/my-policy")
def my_policy(exam_id: int, student=Depends(get_current_student), db: Session = Depends(get_db)):
    item = _policy(db, exam_id, student.id)
    return {
        "extra_minutes": item.extra_minutes if item else 0,
        "extra_attempts": item.extra_attempts if item else 0,
        "session_state": item.session_state if item else "active",
        "total_paused_seconds": item.total_paused_seconds if item else 0,
    }


@router.get("/reports/results-filtered")
def filtered_results(
    exam_id: int | None = None, class_id: int | None = None,
    date_from: datetime | None = None, date_to: datetime | None = None,
    min_score: float = Query(default=0, ge=0, le=10),
    max_score: float = Query(default=10, ge=0, le=10),
    teacher=Depends(get_current_teacher), db: Session = Depends(get_db),
):
    query = db.query(ExamResult, Student, Exam).join(Student, Student.id == ExamResult.student_id).join(Exam, Exam.id == ExamResult.exam_id).filter(
        Exam.created_by == teacher.id, ExamResult.total_score >= min_score, ExamResult.total_score <= max_score,
    )
    if exam_id: query = query.filter(ExamResult.exam_id == exam_id)
    if class_id:
        query = query.join(ClassStudent, ClassStudent.student_id == Student.id).filter(ClassStudent.class_id == class_id)
    if date_from: query = query.filter(ExamResult.finished_at >= date_from)
    if date_to: query = query.filter(ExamResult.finished_at <= date_to)
    return [{
        "result_id": result.id, "exam_id": exam.id, "exam_title": exam.title,
        "student_id": student.id, "student_name": student.full_name,
        "student_code": student.student_code, "score": result.total_score,
        "finished_at": result.finished_at,
    } for result, student, exam in query.order_by(ExamResult.finished_at.desc()).all()]


@router.get("/reports/exams/{exam_id}/class-comparison")
def class_comparison(exam_id: int, teacher=Depends(get_current_teacher), db: Session = Depends(get_db)):
    _teacher_exam(db, exam_id, teacher.id)
    rows = db.query(
        Class.id, Class.name, func.count(ExamResult.id), func.avg(ExamResult.total_score),
        func.min(ExamResult.total_score), func.max(ExamResult.total_score),
    ).join(ClassStudent, ClassStudent.class_id == Class.id).join(
        ExamResult, ExamResult.student_id == ClassStudent.student_id
    ).join(ExamAllowedClass, (ExamAllowedClass.class_id == Class.id) & (ExamAllowedClass.exam_id == ExamResult.exam_id)).filter(
        ExamResult.exam_id == exam_id
    ).group_by(Class.id, Class.name).all()
    return [{"class_id": r[0], "class_name": r[1], "attempts": r[2], "average": round(float(r[3] or 0), 2), "minimum": r[4], "maximum": r[5]} for r in rows]


@router.get("/reports/exams/{exam_id}/attempt-comparison")
def attempt_comparison(exam_id: int, teacher=Depends(get_current_teacher), db: Session = Depends(get_db)):
    _teacher_exam(db, exam_id, teacher.id)
    results = db.query(ExamResult, Student).join(Student).filter(ExamResult.exam_id == exam_id).order_by(Student.id, ExamResult.finished_at).all()
    counters = {}
    response = []
    for result, student in results:
        counters[student.id] = counters.get(student.id, 0) + 1
        response.append({"student_id": student.id, "student_name": student.full_name, "attempt": counters[student.id], "score": result.total_score, "finished_at": result.finished_at})
    return response
