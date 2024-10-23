from pydantic import BaseModel, EmailStr


class MailData(BaseModel):
    receiver: EmailStr
    subject:str
    token: str