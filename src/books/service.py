from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.repository import BookRepository
from src.books.schemas import BookCreateModel, BookCreatedModel, BookModelOut
from src.db.models import Book, User

class BookService:
    def __init__(self, session: AsyncSession):
        self.repository = BookRepository(session)

    async def get_all_books(self, search: str, limit: int, offset: int) -> List[BookModelOut]:
        return await self.repository.get_all_books(search, limit, offset)
    
    async def create_book(self, book_data: BookCreateModel,current_user: User) -> BookCreatedModel:
        book_data_dict = book_data.model_dump()
        new_book = Book(**book_data_dict)
        new_book.users=[current_user]
        new_book.creator_id=current_user.id
        return await self.repository.create_book(new_book)
