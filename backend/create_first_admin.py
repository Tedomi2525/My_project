from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.services.auth_service import AuthService
import sys

# Đảm bảo bảng đã được tạo trước khi insert
# Base.metadata.create_all(bind=engine) 
# (Dòng trên không cần thiết nếu bạn đã chạy server main.py 1 lần rồi)

def create_super_admin():
    db = SessionLocal()
    
    try:
        # 1. Kiểm tra xem đã có admin nào chưa
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("❌ Tài khoản 'admin' đã tồn tại! Không cần tạo lại.")
            return

        # 2. Tạo thông tin Admin
        print("dang tao tk admin...")
        username = "admin"
        password = "admin123" # <--- MẬT KHẨU MẶC ĐỊNH
        
        # Mã hóa mật khẩu bằng logic của hệ thống
        hashed_password = AuthService.get_password_hash(password)
        
        new_admin = User(
            username=username,
            password_hash=hashed_password,
            full_name="Super Administrator",
            email="admin@exam.com",
            role=UserRole.ADMIN # Set quyền to nhất
        )

        # 3. Lưu vào DB
        db.add(new_admin)
        db.commit()
        print(f"✅ Đã tạo thành công Admin!")
        print(f"👉 Username: {username}")
        print(f"👉 Password: {password}")

    except Exception as e:
        print(f"❌ Có lỗi xảy ra: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_super_admin()