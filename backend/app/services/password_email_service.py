import logging
import smtplib
from email.message import EmailMessage

from app.core.config import (
    FRONTEND_URL, SMTP_FROM, SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USE_TLS, SMTP_USER,
)

logger = logging.getLogger(__name__)


def send_password_reset_email(to_email: str, full_name: str, token: str):
    if not (SMTP_HOST and SMTP_FROM and SMTP_USER and SMTP_PASSWORD):
        logger.warning("SMTP is not configured; password reset email was not sent")
        return False
    message = EmailMessage()
    message["Subject"] = "Đặt lại mật khẩu hệ thống thi trắc nghiệm"
    message["From"] = SMTP_FROM
    message["To"] = to_email
    message.set_content(
        f"Xin chào {full_name},\n\n"
        "Mã đặt lại mật khẩu của bạn có hiệu lực trong 30 phút:\n\n"
        f"{token}\n\n"
        f"Mở liên kết: {FRONTEND_URL}/reset-password?token={token}\n\n"
        "Nếu bạn không yêu cầu thao tác này, hãy bỏ qua email."
    )
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
            if SMTP_USE_TLS:
                server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(message)
        return True
    except Exception:
        logger.exception("Failed to send password reset email to %s", to_email)
        return False
