from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.core.config import CORS_ORIGINS
from app.database import engine

# --- IMPORT ROUTERS ---
from app.routers.admins import router as admin_router
from app.routers.teachers import router as teacher_router
from app.routers.students import router as student_router
from app.routers.classrooms import router as class_router
from app.routers.questions import router as question_router
from app.routers.exams import router as exam_router
from app.routers.results import router as result_router
from app.routers.auth import router as auth_router

# Tạo bảng
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Quiz App Backend")

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


@app.get("/")
def root():
    return {"message": "Quiz API is running!"}
