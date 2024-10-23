from typing import List
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from config import settings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.default_admin_email,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER= settings.mail_server,
    MAIL_FROM_NAME=settings.mail_from_name,
    MAIL_STARTTLS=settings.mail_starttls,
    MAIL_SSL_TLS=settings.mail_ssl_tls,
    USE_CREDENTIALS=settings.use_credentials,
    VALIDATE_CERTS=settings.validate_certs,
    TEMPLATE_FOLDER=Path(BASE_DIR, 'templates')
)
mail =FastMail(mail_config)

def create_message(recipients: List[str], subject: str, body: str):
    message = MessageSchema(
        subject=subject,
        recipients= recipients,
        body=body,
        subtype=MessageType.html
    )
    return message

