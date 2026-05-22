import logging
import smtplib
from email.message import EmailMessage

from app.core.config import (
    SMTP_FROM,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USE_TLS,
    SMTP_USER,
)

logger = logging.getLogger(__name__)


class EmailService:
    @staticmethod
    def is_configured() -> bool:
        return bool(SMTP_HOST and SMTP_FROM and SMTP_USER and SMTP_PASSWORD)

    @staticmethod
    def send_account_created_email(
        *,
        to_email: str,
        full_name: str,
        role: str,
        username: str,
        password: str,
    ) -> tuple[bool, str | None]:
        if not EmailService.is_configured():
            error_message = "SMTP is not configured"
            logger.warning("%s; account email was not sent", error_message)
            return False, error_message

        role_label = "Giáo viên" if role == "teacher" else "Sinh viên"
        message = EmailMessage()
        message["Subject"] = "Tài khoản hệ thống thi trắc nghiệm đã được tạo"
        message["From"] = SMTP_FROM
        message["To"] = to_email
        message.set_content(
            "\n".join(
                [
                    f"Xin chào {full_name},",
                    "",
                    f"Tài khoản {role_label.lower()} của bạn đã được admin tạo.",
                    "",
                    f"Tên đăng nhập: {username}",
                    f"Mật khẩu: {password}",
                    "",
                    "Vui lòng đăng nhập và đổi mật khẩu nếu hệ thống hỗ trợ.",
                ]
            )
        )

        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
                if SMTP_USE_TLS:
                    server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(message)
            return True, None
        except Exception as exc:
            logger.exception("Failed to send account created email to %s", to_email)
            return False, str(exc)
