from fastapi import FastAPI
from routes import mail_router
app = FastAPI()

app.include_router(mail_router, prefix="/api/v1/mail",tags=["Mail"] )