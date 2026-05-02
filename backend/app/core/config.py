import os

SECRET_KEY = os.getenv("SECRET_KEY", "bi_mat_khong_duoc_bat_mi_cho_ai_biet")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


def _parse_csv_env(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


DEFAULT_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ORIGINS = _parse_csv_env(
    os.getenv("CORS_ORIGINS", ",".join(DEFAULT_CORS_ORIGINS))
)
