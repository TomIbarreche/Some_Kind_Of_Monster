from fastapi import APIRouter, status, Depends

from src.books.schemas import BookCreateModel
from src.db import get_session
from src.db.models import User
from src.dependencies import get_current_user
from src.requests.service import RequestService
from sqlmodel.ext.asyncio.session import AsyncSession

requests_router = APIRouter()

@requests_router.post("/{book_id}", status_code=status.HTTP_201_CREATED)
async def create_update_book_request(book_id: int,update_data: BookCreateModel, current_user: User = Depends(get_current_user), session : AsyncSession = Depends(get_session)):
    _service =RequestService(session)
    await _service.create_update_book_request(book_id, update_data, current_user, session)    

@requests_router.get("/check_requests/{token}")
async def check_request(token:str, session: AsyncSession = Depends(get_session)):
    _service = RequestService(session)
    data =await _service.check_requests(token)
    return {"data": data}