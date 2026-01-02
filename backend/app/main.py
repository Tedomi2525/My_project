from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, SessionLocal
from app import models
from app.routers import (
    auth, 
    users, 
    classroom, 
    questions, 
    exams, 
    results
)

# 1. Tạo bảng trong Database (nếu chưa có)
# Lệnh này sẽ quét tất cả models đã import trong app/models/__init__.py
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hệ thống Thi Trắc Nghiệm API",
    description="API Backend cho dự án Vue 3 + FastAPI",
    version="1.0.0"
)

# 2. Cấu hình CORS (Quan trọng để Vue gọi được API)
origins = [
    "http://localhost:3000",  # Frontend Vue mặc định
    "http://127.0.0.1:3000",
    "*"                       # Cho phép tất cả (chỉ dùng khi dev)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Đăng ký các Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(classroom.router)
app.include_router(questions.router)
app.include_router(exams.router)
app.include_router(results.router)

# 4. Root Endpoint (Kiểm tra server sống hay chết)
@app.get("/")
def read_root():
    return {"message": "Welcome to Quiz System API", "docs": "/docs"}

# --- TỰ ĐỘNG TẠO TÀI KHOẢN MẪU (SEED DATA) ---
# Hàm này chạy 1 lần khi server khởi động để tạo user admin/teacher/student
@app.on_event("startup")
def create_initial_data():
    db = SessionLocal()
    try:
        # Kiểm tra xem đã có user nào chưa
        if db.query(models.User).count() == 0:
            print("Creating seed data...")
            
            # 1. Tạo Admin
            admin = models.User(
                username="admin",
                password_hash="admin123", # Lưu ý: Thực tế cần hash password
                full_name="Quản Trị Viên",
                email="admin@edu.vn",
                role="admin"
            )
            
            # 2. Tạo Teacher
            teacher = models.User(
                username="teacher",
                password_hash="teacher123",
                full_name="Cô Giáo Lan",
                email="teacher@edu.vn",
                role="teacher"
            )
            
            # 3. Tạo Student
            student = models.User(
                username="student",
                password_hash="student123",
                full_name="Nguyễn Văn A",
                email="student@edu.vn",
                role="student",
                student_code="SV001"
            )
            
            db.add_all([admin, teacher, student])
            db.commit()
            print("--- Đã tạo tài khoản mẫu: admin/admin123, teacher/teacher123, student/student123 ---")
    finally:
        db.close()

# --- CHẠY SERVER ---
# Nếu bạn chạy file này trực tiếp bằng python main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)