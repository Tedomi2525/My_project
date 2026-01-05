from app.database import SessionLocal
from app.models.user import User
from app.services.user_service import UserService

def create_initial_data():
    db = SessionLocal()
    
    # 1. Kiểm tra xem admin đã tồn tại chưa
    user = db.query(User).filter(User.username == "admin").first()
    if user:
        print("⚠️  User 'admin' đã tồn tại!")
        return

    # 2. Tạo user admin mới
    print("⏳ Đang tạo tài khoản Admin...")
    
    # Mã hóa mật khẩu "admin123"
    hashed_password = UserService.get_password_hash("admin123")
    
    admin_user = User(
        username="admin",
        password=hashed_password, # Lưu pass đã mã hóa vào DB
        full_name="Super Admin",
        email="admin@example.com",
        role="admin"
    )

    db.add(admin_user)
    db.commit()
    print("✅ Đã tạo thành công!")
    print("👉 Username: admin")
    print("👉 Password: admin123")
    
    db.close()

if __name__ == "__main__":
    create_initial_data()