from typing import Annotated, List, Optional
from fastapi import APIRouter, Query, status, Depends

from src.books.schemas import BookCreateModel, BookModelOut
from src.db import get_session
from src.db.models import User
from src.dependencies import RoleChecker, get_current_user
from src.enums import Role
from src.requests.schemas import CreateRequestOut
from src.requests.service import RequestService
from sqlmodel.ext.asyncio.session import AsyncSession

requests_router = APIRouter()
content_creator_role_checker =  Depends(RoleChecker([Role.ADMIN.value, Role.CONTENT_CREATOR.value]))
admin_role_checker = Depends(RoleChecker([Role.ADMIN.value]))

@requests_router.post("/{book_id}", status_code=status.HTTP_201_CREATED, response_model=CreateRequestOut)
async def create_update_book_request(book_id: int,update_data: BookCreateModel, current_user: User = Depends(get_current_user), session : AsyncSession = Depends(get_session)):
    _service =RequestService(session)
    return await _service.create_update_book_request(book_id, update_data, current_user, session)    

@requests_router.get("/check_requests/{token}", status_code=status.HTTP_200_OK, response_model=CreateRequestOut, dependencies=[content_creator_role_checker])
async def check_request_from_mail(token:str, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    _service = RequestService(session)
    request = await _service.get_request_from_mail(token, current_user)
    return request

@requests_router.get("/user/{user_id}", status_code=status.HTTP_200_OK, response_model=List[CreateRequestOut], dependencies=[content_creator_role_checker])
async def get_all_user_request(user_id: int, session: AsyncSession = Depends(get_session)):
    _service = RequestService(session)
    requests = await _service.get_requests_for_user(user_id)
    return requests

@requests_router.get("/", status_code=status.HTTP_200_OK, response_model=List[CreateRequestOut], dependencies=[admin_role_checker])
async def get_all_requests(limit: Annotated[int, Query(gt=0,le=100)] = 10, offset: Annotated[int, Query(gt=-1, le=100)]=0, session: AsyncSession = Depends(get_session)):
    _service = RequestService(session)
    return await _service.get_all_requests(limit, offset)

@requests_router.patch("/{request_id}/validate", status_code=status.HTTP_200_OK, response_model=BookModelOut, dependencies=[content_creator_role_checker])
async def validate_request(request_id: int, session: AsyncSession = Depends(get_session), current_user:User = Depends(get_current_user)):
    _service = RequestService(session)
    return await _service.validate_request(request_id, current_user)