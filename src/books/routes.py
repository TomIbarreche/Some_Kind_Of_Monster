from typing import List
from fastapi import Depends, APIRouter, status
from src.books.schemas import BookCreateModel, BookCreatedModel, BookModelOut
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db import get_session
from src.db.models import User
from  src.dependencies import RoleChecker, TokenAccessBearer, get_current_user
from src.enums import Role
from src.books.service import BookService

books_router = APIRouter()
admin_role_checker = RoleChecker([Role.ADMIN])
content_creator_role_checker = RoleChecker([Role.ADMIN.value, Role.CONTENT_CREATOR.value])
access_token_bearer = TokenAccessBearer()

@books_router.get("/", status_code=status.HTTP_200_OK, response_model=List[BookModelOut])
async def get_all_books(
    search: str = "",
    limit:int=10,
    offset:int=0,
    session: AsyncSession = Depends(get_session),
    role_checker: bool = Depends(admin_role_checker),
    token_details: dict = Depends(content_creator_role_checker)
):
    _service = BookService(session)
    return await _service.get_all_books(search, limit, offset)

@books_router.post("/", status_code=status.HTTP_201_CREATED, response_model=BookCreatedModel)
async def create_book(
    book_data: BookCreateModel,
    token_details: dict = Depends(access_token_bearer),
    session: AsyncSession = Depends(get_session),
    role_checker: bool = Depends(content_creator_role_checker),
    current_user: User = Depends(get_current_user)
):
    _service = BookService(session)
    return await _service.create_book(book_data, current_user)
