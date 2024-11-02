from typing import List
from sqlmodel import select
from sqlmodel import Session
from src.books.schemas import BookCreatedModel, BookModelOut
from src.db.models import Book

class BookRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all_books(self, search: str, limit: int, offset: int) -> List[BookModelOut]:
        statement = select(Book).where(Book.name.like('%' +search +'%')).order_by(Book.created_at).offset(offset).limit(limit)
        result = self.session.exec(statement)
        books = result.unique()
        return books
    
    def create_book(self, new_book: Book) ->  BookCreatedModel:
        self.session.add(new_book)
        self.session.commit()
        self.session.refresh(new_book)
        return new_book
    
    def get_book_by_id(self, book_id: int) -> BookModelOut:
        statement = select(Book).where(Book.id == book_id)
        result = self.session.exec(statement)
        book = result.first()
        return book
    
    def update_book(self,book_to_update: Book, book_data_dict: dict) -> BookModelOut:
        for k,v in book_data_dict.items():
            setattr(book_to_update,k,v)
        
        self.session.commit()
        return book_to_update
    
    def delete_book(self, book_to_delete: Book):
        self.session.delete(book_to_delete)
        self.session.commit()
        return {}
