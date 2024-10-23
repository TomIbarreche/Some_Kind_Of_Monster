from fastapi import APIRouter, BackgroundTasks
from schemas import MailData
from service import MailService
mail_router = APIRouter()



@mail_router.post("/send_email")
async def send_email(data: MailData, bg_task: BackgroundTasks):
    _mail_service = MailService()
    await _mail_service.send_email(data, bg_task)
    
