import random
import csv
import io
from collections import defaultdict

from sqlalchemy.orm import Session
from sqlalchemy import exists, or_
from app.models.question import Question
from app.models.question_topic import QuestionTopic
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

        query = db.query(Question).filter(
            or_(
                Question.visibility == "public",
                Question.created_by == teacher_id,
            )
        )

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

    @staticmethod
    def get_topics(db: Session):
        return db.query(QuestionTopic).order_by(QuestionTopic.name.asc()).all()

    @staticmethod
    def create_topic(db: Session, name: str, description: str | None, created_by: int):
        normalized_name = name.strip()
        topic = db.query(QuestionTopic).filter(QuestionTopic.name == normalized_name).first()
        if topic:
            return topic

        topic = QuestionTopic(
            name=normalized_name,
            description=description,
            created_by=created_by,
        )
        db.add(topic)
        db.commit()
        db.refresh(topic)
        return topic

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
                        visibility="public",
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
    def get_questions(db: Session, skip: int = 0, limit: int | None = None):
        query = db.query(Question).offset(skip)
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    @staticmethod
    def get_questions_for_teacher(db: Session, teacher_id: int, skip: int = 0, limit: int | None = None):
        questions = QuestionService._get_accessible_teacher_questions(db, teacher_id)
        if limit is None:
            return questions[skip:]
        return questions[skip: skip + limit]

    @staticmethod
    def can_teacher_access_question(db: Session, question_id: int, teacher_id: int) -> bool:
        question = QuestionService.get_question(db, question_id)
        if not question:
            return False
        return question.visibility == "public" or question.created_by == teacher_id

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

    @staticmethod
    def _generated_content(source_content: str, target_difficulty: str, variant_index: int) -> tuple[str, str]:
        normalized = " ".join(source_content.strip().split())
        templates = {
            QuestionDifficultyLevel.EASY.value: [
                ("Chọn đáp án đúng: {content}", "Biến thể nhận biết từ câu hỏi gốc."),
                ("Câu nào sau đây trả lời đúng cho vấn đề: {content}", "Giữ ở mức nhớ/nhận biết."),
                ("Hãy xác định đáp án đúng cho câu hỏi: {content}", "Gợi ý câu hỏi dễ dựa trên nội dung gốc."),
            ],
            QuestionDifficultyLevel.MEDIUM.value: [
                ("Dựa vào kiến thức liên quan, hãy chọn đáp án phù hợp nhất: {content}", "Tăng lên mức áp dụng cơ bản."),
                ("Khi cần giải thích nội dung sau, đáp án nào là hợp lý nhất: {content}", "Tạo biến thể yêu cầu hiểu và giải thích."),
                ("Áp dụng kiến thức đã học để trả lời: {content}", "Gợi ý câu hỏi trung bình từ câu hỏi gốc."),
            ],
            QuestionDifficultyLevel.HARD.value: [
                ("Trong một tình huống cần vận dụng cao, đáp án nào phù hợp nhất cho vấn đề: {content}", "Tăng độ khó theo hướng vận dụng/suy luận."),
                ("Nếu phải phân tích sâu nội dung sau, lựa chọn nào chính xác nhất: {content}", "Tạo biến thể phân tích từ câu hỏi gốc."),
                ("Hãy suy luận và chọn đáp án tối ưu cho câu hỏi: {content}", "Gợi ý câu hỏi khó dựa trên nội dung gốc."),
            ],
        }
        selected_templates = templates.get(target_difficulty, templates[QuestionDifficultyLevel.EASY.value])
        template, reason = selected_templates[variant_index % len(selected_templates)]
        return template.format(content=normalized), reason

    @staticmethod
    def generate_question_suggestions(
        db: Session,
        teacher_id: int,
        target_difficulty: str,
        count: int,
        topic_id: int | None = None,
    ):
        target_difficulty = str(target_difficulty).upper()
        if target_difficulty not in {level.value for level in QuestionDifficultyLevel}:
            raise ValueError("target_difficulty must be one of EASY, MEDIUM, HARD")

        questions = QuestionService._get_accessible_teacher_questions(db, teacher_id)
        if topic_id is not None:
            questions = [question for question in questions if question.topic_id == topic_id]

        usable_questions = [
            question
            for question in questions
            if question.content and question.options and question.correct_answer
        ]
        if not usable_questions:
            raise ValueError("No suitable questions available for generating suggestions")

        random.shuffle(usable_questions)
        suggestions = []
        seen_content = set()
        max_attempts = max(count * 4, len(usable_questions))

        for attempt_index in range(max_attempts):
            if len(suggestions) >= count:
                break

            source = usable_questions[attempt_index % len(usable_questions)]
            content, reason = QuestionService._generated_content(
                source.content,
                target_difficulty,
                attempt_index,
            )
            content_key = content.strip().lower()
            if content_key in seen_content:
                continue

            seen_content.add(content_key)
            suggestions.append(
                {
                    "content": content,
                    "question_type": source.question_type or "MCQ",
                    "difficulty": target_difficulty,
                    "options": source.options,
                    "correct_answer": source.correct_answer,
                    "topic_id": source.topic_id,
                    "source_question_id": source.id,
                    "source_content": source.content,
                    "reason": reason,
                }
            )

        return {
            "suggestions": suggestions,
            "total_generated": len(suggestions),
        }

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
            
        merged_data = {
            "content": db_question.content,
            "question_type": db_question.question_type,
            "difficulty": getattr(db_question.difficulty, "value", db_question.difficulty),
            "options": db_question.options,
            "correct_answer": db_question.correct_answer,
            "topic_id": db_question.topic_id,
            "visibility": db_question.visibility,
            "created_by": db_question.created_by,
            **question_data,
        }
        validated_question = QuestionCreate(**merged_data)

        for key, value in validated_question.model_dump(exclude={"created_by"}).items():
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
