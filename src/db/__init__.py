from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import create_engine
from src.config import settings
from sqlmodel.ext.asyncio.session import AsyncSession

async_engine = AsyncEngine(
    create_engine(url =settings.database_url)
)

async def get_session():
    with AsyncSession(async_engine) as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]