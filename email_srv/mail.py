from typing import List
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

mail_config = ConnectionConfig(
    MAIL_USERNAME="ibarreche666",
    MAIL_PASSWORD="nfxi orap tqgn zrwt",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_FROM_NAME="FastAPIPlus",
    MAIL_FROM="ibarreche666@gmail.com",
    MAIL_STARTTLS= True,
    MAIL_SSL_TLS= False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS= True,
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

