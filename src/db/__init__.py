from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import SQLModel, create_engine
from src.config import settings
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from src.auth.service import UserService

async_engine = AsyncEngine(
    create_engine(
        url=settings.database_url,
        future=True
    )
)


async def init_db():
    print("Database initialization started")
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    async with AsyncSession(async_engine) as session:
        user_service = UserService(session)
        if await user_service.check_if_admin_exists() == False:
            print("No default admin found. Lets create one")
            await user_service.create_default_admin()
    print("Database after")
    
async def get_session()-> AsyncSession: # type: ignore
    Session = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with Session() as session:
        yield session
        