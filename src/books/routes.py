from typing import List
from fastapi import Depends, APIRouter, status
from src.books.schemas import BookCreateModel, BookCreatedModel, BookModelOut
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db import get_session
from src.db.models import User
from src.dependencies import RoleChecker, TokenAccessBearer, get_current_user
from src.enums import Role
from src.books.service import BookService

books_router = APIRouter()
admin_role_checker = Depends(RoleChecker([Role.ADMIN.value]))
content_creator_role_checker = Depends(RoleChecker([Role.ADMIN.value, Role.CONTENT_CREATOR.value]))
access_token_bearer = Depends(TokenAccessBearer())
@books_router.get("/", status_code=status.HTTP_200_OK, response_model=List[BookModelOut], dependencies=[content_creator_role_checker, access_token_bearer])

async def get_all_books(
    search: str = "",
    limit:int=10,
    offset:int=0,
    session: AsyncSession = Depends(get_session),
):
    _service = BookService(session)
    return await _service.get_all_books(search, limit, offset)

@books_router.post("/", status_code=status.HTTP_201_CREATED, response_model=BookCreatedModel, dependencies=[access_token_bearer, content_creator_role_checker])
async def create_book(
    book_data: BookCreateModel,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    _service = BookService(session)
    return await _service.create_book(book_data, current_user)

@books_router.get("/{book_id}", status_code=status.HTTP_200_OK, response_model=BookModelOut, dependencies=[access_token_bearer])
async def get_book_by_id(book_id: int, session: AsyncSession = Depends(get_session)):
    _service = BookService(session)
    return await _service.get_book_by_id(book_id)

@books_router.patch("/{book_id}", status_code=status.HTTP_200_OK, response_model=BookModelOut, dependencies=[access_token_bearer, content_creator_role_checker])
async def update_book(book_id: int, book_data: BookCreateModel, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    _service = BookService(session)
    return await _service.update_book(book_id, book_data, current_user)
    
@books_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[access_token_bearer, admin_role_checker])
async def delete_book(book_id: int, session: AsyncSession = Depends(get_session)):
    _service = BookService(session)
    return await _service.delete_book(book_id)