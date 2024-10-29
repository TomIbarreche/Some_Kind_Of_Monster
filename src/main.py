from fastapi import FastAPI
from .config import settings
from contextlib import asynccontextmanager
from src.db import init_db
from .routers import registered_routers
from .errors import register_errors

@asynccontextmanager
async def life_span(app:FastAPI):
    print("start")
    await init_db()
    yield

    print("after")

app = FastAPI(
    lifespan=life_span,
    version=settings.api_version,
    title=settings.api_name,
    summary=settings.api_summary,
    contact={
        "name":settings.developer_name,
        "url": settings.developer_profile, 
        "email": settings.developer_email
    }
)

registered_routers(app)
register_errors(app)