from fastapi import FastAPI
from src.auth.routes import auth_router
from src.books.routes import books_router
from src.requests.routes import requests_router
from src.config import settings

def registered_routers(app: FastAPI):
    app.include_router(auth_router,prefix=f"{settings.api_prefix}/auth",tags=["Auth"])
    app.include_router(books_router,prefix=f"{settings.api_prefix}/books",tags=["Books"])
    app.include_router(requests_router,prefix=f"{settings.api_prefix}/requests",tags=["Requests"])
