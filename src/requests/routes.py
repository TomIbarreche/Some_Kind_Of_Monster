from fastapi import APIRouter, status, Depends

from src.books.schemas import BookCreateModel
from src.db import get_session
from src.db.models import User
from src.dependencies import RoleChecker, get_current_user
from src.enums import Role
from src.requests.schemas import CreateRequestOut
from src.requests.service import RequestService
from sqlmodel.ext.asyncio.session import AsyncSession

requests_router = APIRouter()
content_creator_role_checker =  Depends(RoleChecker([Role.ADMIN.value, Role.CONTENT_CREATOR.value]))

@requests_router.post("/{book_id}", status_code=status.HTTP_201_CREATED, response_model=CreateRequestOut)
async def create_update_book_request(book_id: int,update_data: BookCreateModel, current_user: User = Depends(get_current_user), session : AsyncSession = Depends(get_session)):
    _service =RequestService(session)
    return await _service.create_update_book_request(book_id, update_data, current_user, session)    

@requests_router.get("/check_requests/{token}", status_code=status.HTTP_200_OK, response_model=CreateRequestOut, dependencies=[content_creator_role_checker])
async def check_request_from_mail(token:str, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    _service = RequestService(session)
    request =await _service.get_request_from_mail(token, current_user)
    return request