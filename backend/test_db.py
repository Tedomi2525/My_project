from app.database.session import engine

with engine.connect() as conn:
    print("✅ Kết nối MySQL thành công")
