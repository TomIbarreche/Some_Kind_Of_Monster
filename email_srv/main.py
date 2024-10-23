from fastapi import FastAPI
from routes import mail_router
from config import settings
app = FastAPI()

app.include_router(mail_router, prefix=f"{settings.api_prefix}/mail",tags=["Mail"] )