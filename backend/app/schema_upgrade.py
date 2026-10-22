from sqlalchemy import inspect, text


QUESTION_COLUMNS = {
    "image_url": "TEXT NULL",
    "code_snippet": "TEXT NULL",
    "code_language": "VARCHAR(50) NULL",
    "explanation": "TEXT NULL",
}


def apply_compatible_schema_upgrades(engine):
    inspector = inspect(engine)
    if "question" not in inspector.get_table_names():
        return
    existing = {column["name"] for column in inspector.get_columns("question")}
    with engine.begin() as connection:
        for name, ddl in QUESTION_COLUMNS.items():
            if name not in existing:
                connection.execute(text(f"ALTER TABLE question ADD COLUMN {name} {ddl}"))
