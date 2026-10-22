from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.audit_middleware import AuditMiddleware
from app.login_rate_limit_middleware import LoginRateLimitMiddleware

from app import models
from app.core.config import CORS_ORIGINS
from app.database import engine
from app.schema_upgrade import apply_compatible_schema_upgrades

# --- IMPORT ROUTERS ---
from app.routers.admins import router as admin_router
from app.routers.teachers import router as teacher_router
from app.routers.students import router as student_router
from app.routers.classrooms import router as class_router
from app.routers.questions import router as question_router
from app.routers.exams import router as exam_router
from app.routers.results import router as result_router
from app.routers.auth import router as auth_router
from app.routers.account_requests import router as account_request_router
from app.routers.security import router as security_router
from app.routers.data_tools import router as data_tools_router
from app.routers.learning_features import router as learning_features_router

# Tạo bảng
models.Base.metadata.create_all(bind=engine)
apply_compatible_schema_upgrades(engine)

app = FastAPI(title="Quiz App Backend")
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.add_middleware(AuditMiddleware)
app.add_middleware(LoginRateLimitMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- REGISTER ROUTERS ---
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(teacher_router)
app.include_router(student_router)
app.include_router(class_router)
app.include_router(question_router)
app.include_router(exam_router)
app.include_router(result_router)
app.include_router(account_request_router)
app.include_router(security_router)
app.include_router(data_tools_router)
app.include_router(learning_features_router)


@app.get("/")
def root():
    return {"message": "Quiz API is running!"}
