from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import inspect, text

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import models  # noqa: E402
from app.database import SessionLocal, engine  # noqa: E402
from app.models.question import Question  # noqa: E402
from app.models.question_topic import QuestionTopic  # noqa: E402


DEFAULT_TOPICS = [
    ("Toán rời rạc", "Logic, tập hợp, quan hệ, tổ hợp."),
    ("Cơ sở dữ liệu", "SQL, mô hình dữ liệu, chuẩn hóa, transaction."),
    ("Lập trình Python", "Cú pháp, cấu trúc dữ liệu, xử lý lỗi."),
    ("Mạng máy tính", "TCP/IP, HTTP, DNS, bảo mật mạng."),
    ("Hệ điều hành", "Process, thread, memory, file system."),
    ("Cấu trúc dữ liệu", "Array, stack, queue, tree, graph."),
    ("Kỹ thuật phần mềm", "Kiểm thử, thiết kế, quản lý yêu cầu."),
    ("An toàn thông tin", "Mã hóa, xác thực, kiểm soát truy cập."),
]


def ensure_question_columns() -> None:
    inspector = inspect(engine)
    columns = {column["name"] for column in inspector.get_columns("question")}

    with engine.begin() as connection:
        if "topic_id" not in columns:
            connection.execute(text("ALTER TABLE question ADD COLUMN topic_id INT NULL"))
        if "visibility" not in columns:
            connection.execute(
                text("ALTER TABLE question ADD COLUMN visibility VARCHAR(50) NOT NULL DEFAULT 'public'")
            )


def seed_topics_and_assign_questions() -> None:
    db = SessionLocal()
    try:
        topics: list[QuestionTopic] = []
        for name, description in DEFAULT_TOPICS:
            topic = db.query(QuestionTopic).filter(QuestionTopic.name == name).first()
            if not topic:
                topic = QuestionTopic(name=name, description=description, created_by=None)
                db.add(topic)
                db.flush()
            topics.append(topic)

        questions = db.query(Question).order_by(Question.id.asc()).all()
        for index, question in enumerate(questions):
            if not question.visibility:
                question.visibility = "public"
            if question.visibility not in {"public", "private"}:
                question.visibility = "public"
            if question.topic_id is None and topics:
                question.topic_id = topics[index % len(topics)].id

        db.commit()
        print("Question topic migration completed.")
        print(f"Topics available: {len(topics)}")
        print(f"Questions checked: {len(questions)}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main() -> None:
    models.Base.metadata.create_all(bind=engine)
    ensure_question_columns()
    seed_topics_and_assign_questions()


if __name__ == "__main__":
    main()
