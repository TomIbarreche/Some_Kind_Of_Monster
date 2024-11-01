from typing import Annotated, Generator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import SQLModel, Session, create_engine
from src.config import settings
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from src.auth.service import UserService


engine = create_engine(url=settings.database_url)
async def init_db():
    print("Database initialization started")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        user_service = UserService(session)
        if user_service.check_if_admin_exists() == False:
            print("No default admin found. Lets create one")
            user_service.create_default_admin()
    print("Database after")
    
print(settings.database_url)
def get_db():
    with Session(engine) as session:
        yield session