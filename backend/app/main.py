from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 

from app import models 
from app.database import engine

# --- SỬA LẠI PHẦN IMPORT (Import trực tiếp từng file cho an toàn) ---
from app.routers.users import router as user_router
from app.routers.classrooms import router as class_router
from app.routers.questions import router as question_router
from app.routers.exams import router as exam_router
from app.routers.results import router as result_router
from app.routers.auth import router as auth_router 
# from app.routers.admin_users import admin_users_router
# -------------------------------------------------------------------

# Tạo bảng
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Quiz App Backend")

# --- CẤU HÌNH CORS ---
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)
# ---------------------

# --- ĐĂNG KÝ ROUTER (Nhớ thêm auth_router vào đây) ---
app.include_router(auth_router) # <--- Quan trọng: Phải có dòng này mới đăng nhập được!
app.include_router(user_router)
app.include_router(class_router)
app.include_router(question_router)
app.include_router(exam_router)
app.include_router(result_router)
# app.include_router(admin_users_router) 


@app.get("/")
def root():
    return {"message": "Quiz API is running!"}