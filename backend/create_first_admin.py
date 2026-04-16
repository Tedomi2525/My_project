from app.database import SessionLocal
from app.models.admin import Admin
from app.services.account_service import AccountService


def create_initial_data():
    db = SessionLocal()

    admin = db.query(Admin).filter(Admin.username == "admin").first()
    if admin:
        print("User 'admin' đã tồn tại!")
        return

    print("Đang tạo tài khoản Admin...")
    hashed_password = AccountService.get_password_hash("admin123")

    admin_user = Admin(
        username="admin",
        password=hashed_password,
        full_name="Super Admin",
        email="admin@example.com"
    )

    db.add(admin_user)
    db.commit()
    print("Đã tạo thành công!")
    print("Username: admin")
    print("Password: admin123")

    db.close()


if __name__ == "__main__":
    create_initial_data()
