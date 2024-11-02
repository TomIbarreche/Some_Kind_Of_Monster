from typing import List
from sqlmodel import Session
from src.books.repository import BookRepository
from src.books.schemas import BookCreateModel, BookCreatedModel, BookModelOut
from src.db.models import Book, User
from src.enums import Role
from src.errors import BookNotFound, TokenVerificationEmailNotMatch, UpdateNotAllowed, UserVerificationFailed
from src.auth.utils import UrlSerializer

class BookService:
    def __init__(self, session: Session):
        self.repository = BookRepository(session)

    async def get_all_books(self, search: str, limit: int, offset: int) -> List[BookModelOut]:
        return self.repository.get_all_books(search, limit, offset)
    
    async def create_book(self, book_data: BookCreateModel,current_user: User) -> BookCreatedModel:
        book_data_dict = book_data.model_dump()
        new_book = Book(**book_data_dict)
        new_book.users=[current_user]
        new_book.creator_id=current_user.id
        return self.repository.create_book(new_book)
    
    async def get_book_by_id(self, book_id: int) -> BookModelOut:
        book = self.repository.get_book_by_id(book_id)
        if book is None:
            raise BookNotFound(info={"error": "Book with this Id not found", "data":f"Book Id: {book_id}"})
        
        return book

    async def update_book(self, book_id: int, book_data: BookCreateModel, current_user: User) -> BookModelOut:
        book_to_update = await self.get_book_by_id(book_id)
        if current_user.role != Role.ADMIN.value and current_user.id != book_to_update.creator_id:
            raise UpdateNotAllowed(info={"error": "You are not authorized to update a book you dont created", "data": f"Book ID: {book_id}"})
        
        book_data_dict = book_data.model_dump()
        return self.repository.update_book(book_to_update, book_data_dict)
    
    async def delete_book(self, book_id: int):
        book_to_delete = await self.get_book_by_id(book_id)
        return self.repository.delete_book(book_to_delete)
    
    async def get_book_from_token(self, token: str, current_user: User) -> BookModelOut:
        try:
            token_data = UrlSerializer.decode_url_safe_token(token)
            user_email = token_data.get("email")
            book_id = token_data.get("book_id")
        except Exception:
            raise UserVerificationFailed(info={"error": "Can't access data from token verification"})
        
        if current_user.email != user_email:
            raise TokenVerificationEmailNotMatch(info={"error": "This book dont belong to the current_user", "data":f"Book owner email: {user_email}"})
        
        book = await self.get_book_by_id(book_id)

        return book
        
        
