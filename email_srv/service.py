from fastapi import BackgroundTasks
from mail import create_message, mail
from schemas import MailData
from config import settings
class MailService:

    async def send_email(self, mail_data: MailData, bg_task: BackgroundTasks):
        body = self.create_body(mail_data.subject, mail_data.token)
        message = create_message([mail_data.receiver], mail_data.subject, body)
        bg_task.add_task(mail.send_message, message)

    def create_body(self, subject:str, token:str) -> str:
        if subject == settings.update_request_mail_subject:
            link = f"http://{settings.domain_name}/{settings.api_prefix}/requests/check_request/{token}"
            body = f"""
                <h1>You have a new book update request</h1>
                <p>Follow this link <a href={link}>link</a> to check this request </p>
                """
        elif subject == settings.verified_mail_subject:
            link = f"http://{settings.domain_name}/{settings.api_prefix}/auth/verify/{token}"
            body = f"""
            <h1>Please verify your email</h1>
            <p>Follow this <a href={link}>link</a> to verify your email</p>
            """
        else:
            link = f"http://{settings.domain_name}/{settings.api_prefix}/auth/password_reset_confirm/{token}"
            body = f"""
            <h1>Reset your password</h1>
            <p>Follow this <a href={link}>link</a> to reset your password </p>
            """
        return body