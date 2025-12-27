from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base # Import thêm declarative_base
from typing import Generator
import os
from dotenv import load_dotenv

# Load biến môi trường từ .env
load_dotenv()

# Xử lý trường hợp quên set biến môi trường để tránh lỗi NoneType
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '') # Mặc định rỗng nếu không có
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME', 'exam_system')

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Tạo engine
engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)

# Tạo session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# --- QUAN TRỌNG: Phải có cái này thì Models mới hoạt động ---
Base = declarative_base()

# Dependency generator
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()