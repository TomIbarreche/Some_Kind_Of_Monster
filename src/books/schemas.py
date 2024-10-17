from datetime import date, datetime
from typing import List
from pydantic import BaseModel
from src.auth.schemas import UserOutModel

class BookModelOut(BaseModel):
    id: int
    name: str
    published_date: date
    author: str
    editor: str
    is_omnibus: bool
    users: List["UserOutModel"]
    creator_id: int

class BookCreatedModel(BaseModel):
    id: int
    name: str
    published_date: date
    author: str
    editor: str
    is_omnibus: bool
    created_at: datetime
    updated_at: datetime
    users: List["UserOutModel"]
    creator_id: int


class BookCreateModel(BaseModel):
    name: str
    published_date: date
    author: str
    editor: str
    is_omnibus: bool
