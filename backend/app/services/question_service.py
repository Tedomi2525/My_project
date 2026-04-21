import random
import csv
import io
from collections import defaultdict

from sqlalchemy.orm import Session
from sqlalchemy import exists
from app.models.question import Question
from app.models.question import DifficultyLevel as QuestionDifficultyLevel
from app.models.teacher import Teacher
from app.schemas.question import QuestionCreate
from typing import Dict, Any, List

class QuestionService:
    CSV_REQUIRED_COLUMNS = {
        "content",
        "difficulty",
        "option_a",
        "option_b",
        "option_c",
        "option_d",
        "correct_answer",
    }

    @staticmethod
    def _get_accessible_teacher_questions(db: Session, teacher_id: int):
        teacher_count = db.query(Teacher).count()

        query = db.query(Question).filter(Question.created_by == teacher_id)

        # Backward compatibility:
        # some legacy questions were created with a stale/non-existent teacher id.
        # If the system currently has a single teacher, allow that teacher to keep using
        # those orphaned questions so random exam generation still works.
        if teacher_count == 1:
            query = db.query(Question).filter(
                (Question.created_by == teacher_id) |
                (~exists().where(Teacher.id == Question.created_by))
            )

        return query.all()

    # --- CREATE ---
    @staticmethod
    def create_question(db: Session, question_in: QuestionCreate):
        db_question = Question(**question_in.model_dump())
        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        return db_question

    @staticmethod
    def import_questions_from_csv(db: Session, teacher_id: int, csv_content: str):
        normalized_content = csv_content.lstrip("\ufeff").strip()
        if not normalized_content:
            raise ValueError("CSV file is empty")

        reader = csv.DictReader(io.StringIO(normalized_content))
        headers = reader.fieldnames or []
        normalized_headers = {str(header).strip().lower() for header in headers if header}
        missing_columns = sorted(QuestionService.CSV_REQUIRED_COLUMNS - normalized_headers)
        if missing_columns:
            raise ValueError(
                "CSV is missing required columns: " + ", ".join(missing_columns)
            )

        imported_questions: List[Question] = []
        errors: List[Dict[str, Any]] = []

        for row_number, raw_row in enumerate(reader, start=2):
            row = {
                str(key).strip().lower(): (value.strip() if isinstance(value, str) else value)
                for key, value in raw_row.items()
                if key
            }

            if not any((value or "").strip() for value in row.values() if isinstance(value, str)):
                continue

            try:
                difficulty = str(row.get("difficulty", "EASY")).upper()
                if difficulty not in {level.value for level in QuestionDifficultyLevel}:
                    raise ValueError("difficulty must be one of EASY, MEDIUM, HARD")

                correct_answer = str(row.get("correct_answer", "")).upper()
                if correct_answer not in {"A", "B", "C", "D"}:
                    raise ValueError("correct_answer must be one of A, B, C, D")

                content = str(row.get("content", "")).strip()
                if not content:
                    raise ValueError("content is required")

                options = {
                    "A": str(row.get("option_a", "")).strip(),
                    "B": str(row.get("option_b", "")).strip(),
                    "C": str(row.get("option_c", "")).strip(),
                    "D": str(row.get("option_d", "")).strip(),
                }
                empty_options = [key for key, value in options.items() if not value]
                if empty_options:
                    raise ValueError(
                        "options cannot be empty for: " + ", ".join(empty_options)
                    )

                imported_questions.append(
                    Question(
                        content=content,
                        question_type="MCQ",
                        difficulty=QuestionDifficultyLevel(difficulty),
                        options=options,
                        correct_answer=correct_answer,
                        created_by=teacher_id,
                    )
                )
            except ValueError as exc:
                errors.append({"row": row_number, "message": str(exc)})

        if not imported_questions and errors:
            return {
                "imported_count": 0,
                "total_rows": max(len(errors), 0),
                "errors": errors,
            }

        if imported_questions:
            db.add_all(imported_questions)
            db.commit()

        return {
            "imported_count": len(imported_questions),
            "total_rows": len(imported_questions) + len(errors),
            "errors": errors,
        }
    
    # --- READ ---
    @staticmethod
    def get_question(db: Session, question_id: int):
        return db.query(Question).filter(Question.id == question_id).first()

    @staticmethod
    def get_questions(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Question).offset(skip).limit(limit).all()

    @staticmethod
    def get_questions_for_teacher(db: Session, teacher_id: int, skip: int = 0, limit: int = 100):
        questions = QuestionService._get_accessible_teacher_questions(db, teacher_id)
        return questions[skip: skip + limit]

    @staticmethod
    def get_random_questions_by_difficulty(
        db: Session,
        teacher_id: int,
        easy_count: int = 0,
        medium_count: int = 0,
        hard_count: int = 0,
    ):
        requested_counts = {
            QuestionDifficultyLevel.EASY.value: easy_count,
            QuestionDifficultyLevel.MEDIUM.value: medium_count,
            QuestionDifficultyLevel.HARD.value: hard_count,
        }

        questions = QuestionService._get_accessible_teacher_questions(db, teacher_id)

        grouped_questions = defaultdict(list)
        for question in questions:
            difficulty = getattr(question.difficulty, "value", question.difficulty)
            grouped_questions[str(difficulty)].append(question)

        selected_ids = []
        shortage_messages = []

        for difficulty, requested_count in requested_counts.items():
            if requested_count <= 0:
                continue

            pool = grouped_questions.get(difficulty, [])
            if len(pool) < requested_count:
                shortage_messages.append(
                    f"{difficulty}: need {requested_count}, only {len(pool)} available"
                )
                continue

            sampled_questions = random.sample(pool, requested_count)
            selected_ids.extend(question.id for question in sampled_questions)

        if shortage_messages:
            raise ValueError("; ".join(shortage_messages))

        random.shuffle(selected_ids)
        return selected_ids

    # --- UPDATE ---
    @staticmethod
    def update_question(db: Session, question_id: int, question_data: Dict[str, Any]):
        """
        question_data là dictionary chứa các field cần sửa.
        VD: {"content": "Câu hỏi mới", "correct_answer": "B"}
        """
        db_question = db.query(Question).filter(Question.id == question_id).first()
        if not db_question:
            return None
            
        for key, value in question_data.items():
            setattr(db_question, key, value)
            
        db.commit()
        db.refresh(db_question)
        return db_question

    # --- DELETE ---
    @staticmethod
    def delete_question(db: Session, question_id: int):
        db_question = db.query(Question).filter(Question.id == question_id).first()
        if db_question:
            db.delete(db_question)
            db.commit()
            return True
        return False
