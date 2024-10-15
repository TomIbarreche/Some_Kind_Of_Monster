from fastapi import FastAPI
from .config import settings
from contextlib import asynccontextmanager

@asynccontextmanager
async def life_span(app:FastAPI):
    print("start")
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





