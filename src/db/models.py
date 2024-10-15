from datetime import date, datetime
from typing import List
from pydantic import EmailStr
from sqlalchemy import Column
from sqlmodel import Field, SQLModel
import sqlalchemy.dialects.postgresql as pg


class CulturalProductBase(SQLModel):
    name: str = Field(index=True)
    published_date: date

class Book(CulturalProductBase, table=True):
    __tablename__ = "books"
    id: int = Field(default=None, primary_key=True)
    author: str
    editor: str
    is_omnibus: bool = Field(default=False)
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP,default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP,default=datetime.now))


class User(SQLModel, table=True):
    __tablename__="users"
    id: int = Field(default=None, primary_key=True)
    username: str = Field(nullable=False, max_length=12, min_length=3, unique=True)
    email: EmailStr = Field(nullable=False,unique=True)
    first_name: str
    last_name: str
    date_of_birth: date
    is_verified: bool = Field(default=False)
    role: List[str] = Field(default=["user"])
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP,default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP,default=datetime.now))