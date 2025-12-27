import bcrypt

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        So sánh mật khẩu nhập vào với mã hóa trong DB.
        bcrypt yêu cầu dữ liệu phải là dạng bytes (b'...') chứ không phải string.
        """
        # Chuyển đổi password người dùng nhập sang bytes
        password_byte_enc = plain_password.encode('utf-8')
        
        # Chuyển đổi hash từ DB sang bytes (nếu nó đang là string)
        hashed_password_byte_enc = hashed_password.encode('utf-8')
        
        # Kiểm tra
        return bcrypt.checkpw(password_byte_enc, hashed_password_byte_enc)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        Mã hóa mật khẩu để lưu vào DB.
        """
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(pwd_bytes, salt)
        
        # Trả về dạng string để lưu vào Database
        return hashed_password.decode('utf-8')