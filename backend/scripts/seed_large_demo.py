from __future__ import annotations

import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import models  # noqa: E402
from app.database import SessionLocal, engine  # noqa: E402
from app.models.class_student import ClassStudent  # noqa: E402
from app.models.classroom import Class  # noqa: E402
from app.models.exam import Exam  # noqa: E402
from app.models.exam_allowed_class import ExamAllowedClass  # noqa: E402
from app.models.exam_question import ExamQuestion  # noqa: E402
from app.models.question import DifficultyLevel, Question  # noqa: E402
from app.models.question_topic import QuestionTopic  # noqa: E402
from app.models.student import Student  # noqa: E402
from app.models.teacher import Teacher  # noqa: E402
from app.services.account_service import AccountService  # noqa: E402


TEACHER_COUNT = 10
STUDENT_COUNT = 200
CLASS_COUNT = 14
QUESTION_COUNT = 210
EXAM_COUNT = 10
TEACHER_ID_BASE = 900000
STUDENT_ID_BASE = 910000
TOPIC_NAMES = [
    "Toán rời rạc",
    "Cơ sở dữ liệu",
    "Lập trình Python",
    "Mạng máy tính",
    "Hệ điều hành",
    "Cấu trúc dữ liệu",
    "Kỹ thuật phần mềm",
    "An toàn thông tin",
]


def ensure_legacy_user(
    db,
    *,
    user_id: int,
    username: str,
    email: str,
    password: str,
    full_name: str,
    role: str,
    student_code: str | None = None,
) -> None:
    AccountService.sync_legacy_user(
        db,
        user_id=user_id,
        username=username,
        email=email,
        password=password,
        full_name=full_name,
        role=role,
        student_code=student_code,
    )


def get_or_create_teacher(db, index: int) -> Teacher:
    teacher_id = TEACHER_ID_BASE + index
    username = f"GV{teacher_id:06d}"
    legacy_username = f"loadtest_gv_{index:02d}"
    email = f"{username}@edu.com"
    full_name = f"Giáo viên Demo {index:02d}"
    password = f"{username}@"
    teacher = (
        db.query(Teacher)
        .filter((Teacher.id == teacher_id) | (Teacher.username.in_([username, legacy_username])))
        .first()
    )
    if teacher:
        teacher.id = teacher_id
        teacher.username = username
        teacher.email = email
        teacher.password = AccountService.get_password_hash(password)
        teacher.full_name = full_name
        ensure_legacy_user(
            db,
            user_id=teacher.id,
            username=teacher.username,
            email=teacher.email,
            password=teacher.password,
            full_name=teacher.full_name,
            role="teacher",
        )
        return teacher

    hashed_password = AccountService.get_password_hash(password)
    ensure_legacy_user(
        db,
        user_id=teacher_id,
        username=username,
        email=email,
        password=hashed_password,
        full_name=full_name,
        role="teacher",
    )
    teacher = Teacher(
        id=teacher_id,
        username=username,
        email=email,
        password=hashed_password,
        full_name=full_name,
    )
    db.add(teacher)
    db.flush()
    return teacher


def get_or_create_student(db, index: int) -> Student:
    student_id = STUDENT_ID_BASE + index
    username = f"SV{student_id:06d}"
    legacy_username = f"loadtest_sv_{index:03d}"
    email = f"{username}@edu.com"
    password = f"{username}@"
    hashed_password = AccountService.get_password_hash(password)
    student = (
        db.query(Student)
        .filter((Student.id == student_id) | (Student.username.in_([username, legacy_username])))
        .first()
    )
    if student:
        student.id = student_id
        student.username = username
        student.email = email
        student.password = hashed_password
        student.full_name = f"Sinh viên Demo {index:03d}"
        student.student_code = username
        ensure_legacy_user(
            db,
            user_id=student.id,
            username=student.username,
            email=student.email,
            password=student.password,
            full_name=student.full_name,
            role="student",
            student_code=student.student_code,
        )
        return student

    student = Student(
        id=student_id,
        username=username,
        email=email,
        password=hashed_password,
        full_name=f"Sinh viên Demo {index:03d}",
        student_code=username,
    )
    db.add(student)
    db.flush()
    ensure_legacy_user(
        db,
        user_id=student.id,
        username=student.username,
        email=student.email,
        password=student.password,
        full_name=student.full_name,
        role="student",
        student_code=student.student_code,
    )
    return student


def get_or_create_class(db, index: int, teacher: Teacher) -> Class:
    name = f"LOADTEST-Lớp {index:02d}"
    class_ = db.query(Class).filter(Class.name == name).first()
    if class_:
        return class_

    class_ = Class(
        name=name,
        description=f"Lớp dữ liệu lớn demo {index:02d}",
        teacher_id=teacher.id,
    )
    db.add(class_)
    db.flush()
    return class_


def ensure_class_student(db, class_id: int, student_id: int) -> None:
    exists = (
        db.query(ClassStudent)
        .filter(ClassStudent.class_id == class_id, ClassStudent.student_id == student_id)
        .first()
    )
    if exists:
        return

    db.add(ClassStudent(class_id=class_id, student_id=student_id))


def question_payload(index: int) -> tuple[str, str, dict[str, str], str, DifficultyLevel]:
    difficulty_cycle = [DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD]
    difficulty = difficulty_cycle[index % len(difficulty_cycle)]

    if index % 5 == 0:
        option_count = 5 + (index % 3)
        keys = [chr(65 + offset) for offset in range(option_count)]
        correct_keys = keys[: 2 + (index % 3)]
        options = {
            key: f"Lựa chọn {key} cho câu nhiều đáp án #{index:03d}"
            for key in keys
        }
        return (
            f"Câu hỏi nhiều đáp án #{index:03d}: chọn các phương án đúng.",
            "MULTI_SELECT",
            options,
            ",".join(correct_keys),
            difficulty,
        )

    correct_key = chr(65 + (index % 4))
    options = {
        "A": f"Phương án A của câu #{index:03d}",
        "B": f"Phương án B của câu #{index:03d}",
        "C": f"Phương án C của câu #{index:03d}",
        "D": f"Phương án D của câu #{index:03d}",
    }
    return (
        f"Câu hỏi trắc nghiệm #{index:03d}: chọn một đáp án đúng.",
        "MCQ",
        options,
        correct_key,
        difficulty,
    )


def get_or_create_question(db, index: int, teacher: Teacher, topic: QuestionTopic) -> Question:
    marker = f"[LOADTEST-Q{index:03d}]"
    question = db.query(Question).filter(Question.content.like(f"{marker}%")).first()
    if question:
        question.topic_id = topic.id
        question.visibility = "public"
        return question

    content, question_type, options, correct_answer, difficulty = question_payload(index)
    question = Question(
        content=f"{marker} {content}",
        question_type=question_type,
        difficulty=difficulty,
        options=options,
        correct_answer=correct_answer,
        topic_id=topic.id,
        visibility="public",
        created_by=teacher.id,
    )
    db.add(question)
    db.flush()
    return question


def get_or_create_exam(db, index: int, teacher: Teacher) -> Exam:
    title = f"LOADTEST-Đề thi {index:02d}"
    exam = db.query(Exam).filter(Exam.title == title).first()
    if exam:
        return exam

    now = datetime.now()
    exam = Exam(
        title=title,
        description=f"Đề thi demo dữ liệu lớn số {index:02d}",
        duration_minutes=45 + (index % 4) * 15,
        start_time=now - timedelta(days=1),
        end_time=now + timedelta(days=30),
        password=None,
        status="published",
        created_by=teacher.id,
        allow_view_answers=True,
        max_attempts=1,
        shuffle_questions=True,
        shuffle_options=True,
    )
    db.add(exam)
    db.flush()
    return exam


def ensure_exam_question(db, exam_id: int, question_id: int) -> None:
    exists = (
        db.query(ExamQuestion)
        .filter(ExamQuestion.exam_id == exam_id, ExamQuestion.question_id == question_id)
        .first()
    )
    if exists:
        return
    db.add(ExamQuestion(exam_id=exam_id, question_id=question_id))


def ensure_exam_class(db, exam_id: int, class_id: int) -> None:
    exists = (
        db.query(ExamAllowedClass)
        .filter(ExamAllowedClass.exam_id == exam_id, ExamAllowedClass.class_id == class_id)
        .first()
    )
    if exists:
        return
    db.add(ExamAllowedClass(exam_id=exam_id, class_id=class_id))


def get_or_create_topic(db, name: str) -> QuestionTopic:
    topic = db.query(QuestionTopic).filter(QuestionTopic.name == name).first()
    if topic:
        return topic

    topic = QuestionTopic(name=name, description=f"Chủ đề demo: {name}", created_by=None)
    db.add(topic)
    db.flush()
    return topic


def main() -> None:
    models.Base.metadata.create_all(bind=engine)

    random.seed(20260524)
    db = SessionLocal()
    try:
        teachers = [get_or_create_teacher(db, index) for index in range(1, TEACHER_COUNT + 1)]
        students = [get_or_create_student(db, index) for index in range(1, STUDENT_COUNT + 1)]
        topics = [get_or_create_topic(db, name) for name in TOPIC_NAMES]
        classes = [
            get_or_create_class(db, index, teachers[(index - 1) % len(teachers)])
            for index in range(1, CLASS_COUNT + 1)
        ]

        for index, student in enumerate(students):
            primary_class = classes[index % len(classes)]
            ensure_class_student(db, primary_class.id, student.id)
            if index % 5 == 0:
                secondary_class = classes[(index + 3) % len(classes)]
                ensure_class_student(db, secondary_class.id, student.id)

        questions = [
            get_or_create_question(
                db,
                index,
                teachers[(index - 1) % len(teachers)],
                topics[(index - 1) % len(topics)],
            )
            for index in range(1, QUESTION_COUNT + 1)
        ]

        exams = [
            get_or_create_exam(db, index, teachers[(index - 1) % len(teachers)])
            for index in range(1, EXAM_COUNT + 1)
        ]

        for index, exam in enumerate(exams):
            owned_questions = [q for q in questions if q.created_by == exam.created_by]
            extra_questions = questions[index * 7 : index * 7 + 15]
            selected_questions = (owned_questions[:20] + extra_questions)[:30]
            for question in selected_questions:
                ensure_exam_question(db, exam.id, question.id)

            ensure_exam_class(db, exam.id, classes[index % len(classes)].id)
            ensure_exam_class(db, exam.id, classes[(index + 1) % len(classes)].id)

        db.commit()

        print("Seed large demo completed.")
        print(f"Teachers: {TEACHER_COUNT}, Students: {STUDENT_COUNT}, Classes: {CLASS_COUNT}")
        print(f"Questions: {QUESTION_COUNT}, Exams: {EXAM_COUNT}")
        print("Demo accounts follow the project code convention.")
        print("Example teacher login: GV900001 / GV900001@")
        print("Example student login: SV910001 / SV910001@")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
