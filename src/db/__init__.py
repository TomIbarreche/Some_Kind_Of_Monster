from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import create_engine
from src.config import settings
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

async_engine = AsyncEngine(
    create_engine(url =settings.database_url)
)

async def init_db():
    print("Database initialization started")
    
async def get_session() ->AsyncSession: # type: ignore
    """
    Create database session
    Yield:
        Session: The database session
    """
    Session = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with Session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]