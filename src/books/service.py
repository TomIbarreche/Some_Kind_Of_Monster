from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.repository import BookRepository
from src.books.schemas import BookModelOut

class BookService:
    def __init__(self, session: AsyncSession):
        self.repository = BookRepository(session)

    async def get_all_books(self, search: str, limit: int, offset: int) -> List[BookModelOut]:
        return await self.repository.get_all_books(search, limit, offset)
