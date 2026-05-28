from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import text

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.database import SessionLocal  # noqa: E402


def main() -> None:
    db = SessionLocal()
    try:
        duplicate_questions = db.execute(
            text(
                """
                SELECT COALESCE(SUM(duplicate_count - 1), 0)
                FROM (
                    SELECT COUNT(*) AS duplicate_count
                    FROM exam_question
                    GROUP BY exam_id, question_id
                    HAVING COUNT(*) > 1
                ) duplicates
                """
            )
        ).scalar()

        duplicate_classes = db.execute(
            text(
                """
                SELECT COALESCE(SUM(duplicate_count - 1), 0)
                FROM (
                    SELECT COUNT(*) AS duplicate_count
                    FROM exam_allowed_class
                    GROUP BY exam_id, class_id
                    HAVING COUNT(*) > 1
                ) duplicates
                """
            )
        ).scalar()

        db.execute(
            text(
                """
                DELETE eq
                FROM exam_question eq
                JOIN (
                    SELECT exam_id, question_id, MIN(id) AS keep_id
                    FROM exam_question
                    GROUP BY exam_id, question_id
                    HAVING COUNT(*) > 1
                ) duplicates
                    ON duplicates.exam_id = eq.exam_id
                    AND duplicates.question_id = eq.question_id
                WHERE eq.id <> duplicates.keep_id
                """
            )
        )

        db.execute(
            text(
                """
                DELETE eac
                FROM exam_allowed_class eac
                JOIN (
                    SELECT exam_id, class_id, MIN(id) AS keep_id
                    FROM exam_allowed_class
                    GROUP BY exam_id, class_id
                    HAVING COUNT(*) > 1
                ) duplicates
                    ON duplicates.exam_id = eac.exam_id
                    AND duplicates.class_id = eac.class_id
                WHERE eac.id <> duplicates.keep_id
                """
            )
        )

        db.commit()
        print(f"Removed duplicate exam_question rows: {int(duplicate_questions or 0)}")
        print(f"Removed duplicate exam_allowed_class rows: {int(duplicate_classes or 0)}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
