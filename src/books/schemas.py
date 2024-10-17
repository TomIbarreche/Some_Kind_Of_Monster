from datetime import date, datetime
from pydantic import BaseModel


class BookModelOut(BaseModel):
    id: int
    name: str
    published_date: date
    author: str
    editor: str
    is_omnibus: bool

class BookCreatedModel(BaseModel):
    id: int
    name: str
    published_date: date
    author: str
    editor: str
    is_omnibus: bool
    created_at: datetime
    updated_at: datetime

class BookCreateModel(BaseModel):
    name: str
    published_date: date
    author: str
    editor: str
    is_omnibus: bool