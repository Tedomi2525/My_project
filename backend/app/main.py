from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, users, classrooms, questions, exams, results

# Tự động tạo bảng nếu chưa có (Chỉ dùng cho dev, prod nên dùng Alembic migration)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Online Exam System API",
    description="API cho hệ thống thi trắc nghiệm trực tuyến",
    version="1.0.0"
)

# Cấu hình CORS (Cho phép VueJS gọi API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Trong production nên đổi thành ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký các Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(classrooms.router)
app.include_router(questions.router)
app.include_router(exams.router)
app.include_router(results.router)

@app.get("/")
def root():
    return {"message": "Welcome to Online Exam System API"}