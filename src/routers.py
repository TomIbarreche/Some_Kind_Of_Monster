from fastapi import FastAPI
from src.auth.routes import auth_router
from src.config import settings

def registered_routers(app: FastAPI):
    app.include_router(auth_router,prefix=f"{settings.api_prefix}/auth",tags=["Auth"])