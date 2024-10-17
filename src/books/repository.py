from typing import List
from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.books.schemas import BookCreatedModel, BookModelOut
from src.db.models import Book

class BookRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_books(self, search: str, limit: int, offset: int) -> List[BookModelOut]:
        statement = select(Book).where(Book.name.like('%' +search +'%')).order_by(Book.created_at).limit(limit).offset(offset)
        result = await self.session.exec(statement)
        books = result.all()
        return books
    
    async def create_book(self, new_book: Book) ->  BookCreatedModel:
        self.session.add(new_book)
        await self.session.commit()
        await self.session.refresh(new_book)
        return new_book