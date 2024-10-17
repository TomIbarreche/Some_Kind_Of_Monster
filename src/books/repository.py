from typing import List
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.books.schemas import BookCreatedModel, BookModelOut
from src.db.models import Book

class BookRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_books(self, search: str, limit: int, offset: int) -> List[BookModelOut]:
        statement = select(Book).where(Book.name.like('%' +search +'%')).order_by(Book.created_at).offset(offset).limit(limit)
        result = await self.session.exec(statement)
        books = result.unique()
        return books
    
    async def create_book(self, new_book: Book) ->  BookCreatedModel:
        self.session.add(new_book)
        await self.session.commit()
        await self.session.refresh(new_book)
        return new_book
    
    async def get_book_by_id(self, book_id: int) -> BookModelOut:
        statement = select(Book).where(Book.id == book_id)
        result = await self.session.exec(statement)
        book = result.first()
        return book
    
    async def update_book(self,book_to_update: Book, book_data_dict: dict) -> BookModelOut:
        for k,v in book_data_dict.items():
            setattr(book_to_update,k,v)
        
        await self.session.commit()
        return book_to_update
    
    async def delete_book(self, book_to_delete: Book):
        await self.session.delete(book_to_delete)
        await self.session.commit()
        return {}
