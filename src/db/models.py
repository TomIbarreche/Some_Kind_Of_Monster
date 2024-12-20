from sqlalchemy import Column, Integer, String
from pydantic import EmailStr
from sqlalchemy.ext.declarative import declarative_base
from datetime import date, datetime
from typing import Optional
from pydantic import EmailStr
from sqlalchemy import Column
from sqlmodel import Field, Relationship, SQLModel
import sqlalchemy.dialects.postgresql as pg

class CulturalProductBase(SQLModel):
    name: str = Field(index=True)
    published_date: date

class UserBookLink(SQLModel, table=True):
    __table_name__="user_book"

    book_id: int | None = Field(default=None, foreign_key="books.id", primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="users.id", primary_key=True)

class Book(CulturalProductBase, table=True):
    __tablename__ = "books"
    id: int = Field(default=None, primary_key=True)
    author: str
    editor: str
    is_omnibus: bool = Field(default=False)
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP,default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP,default=datetime.now))
    creator_id: int = Field(nullable=False)
    users: list["User"] = Relationship(back_populates="books", link_model=UserBookLink, sa_relationship_kwargs={'lazy': 'joined'})
    
class User(SQLModel, table=True):
    __tablename__="users"
    id: int = Field(default=None, primary_key=True)
    username: str = Field(nullable=False, max_length=12, min_length=3, unique=True)
    email: EmailStr = Field(nullable=False,unique=True)
    first_name: str
    last_name: str
    date_of_birth: date
    is_verified: bool = Field(default=False)
    password_hash: str = Field(exclude=True)
    role: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="user"))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP,default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP,default=datetime.now))
    books: list["Book"] = Relationship(back_populates="users", link_model=UserBookLink, sa_relationship_kwargs={'lazy': 'joined'})
    requests: list["Request"] = Relationship(sa_relationship_kwargs={"primaryjoin":"User.id==Request.owner_id", "lazy":"joined"})

class Request(SQLModel, table=True):
    __tablename__="requests"
    id: int = Field(default=None, primary_key=True)
    owner_id: Optional[int] = Field(default=None, foreign_key="users.id")
    owner: User = Relationship(sa_relationship_kwargs={"primaryjoin": "Request.owner_id==User.id", "lazy":"joined"})
    requester_id: Optional[int] = Field(default=None, foreign_key="users.id")
    requester: User = Relationship(sa_relationship_kwargs={"primaryjoin": "Request.requester_id==User.id", "lazy":"joined"})
    book_update_data: str
    book_id: Optional[int] = Field(default=None, foreign_key="books.id")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP,default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP,default=datetime.now))
    status: str