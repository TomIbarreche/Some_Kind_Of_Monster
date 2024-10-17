from typing import List
from fastapi import APIRouter, Depends,status
from fastapi.security import  OAuth2PasswordBearer
from src.auth.schemas import NewCreatedUserModel, UserCreationModel, UserLoginModel, UserOutModel, UserOutModelWithBooks, UserUpdateModel, UserUpdateRoleModel
from src.auth.service import UserService
from src.db import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.models import User
from src.dependencies import TokenAccessBearer, get_current_user, RoleChecker
from src.enums import Role

auth_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
access_token_bearer = Depends(TokenAccessBearer())
admin_role_checker =  Depends(RoleChecker([Role.ADMIN.value]))

@auth_router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=NewCreatedUserModel)
async def create_user(user_data: UserCreationModel, session: AsyncSession = Depends(get_session)):
    _service = UserService(session)
    return await _service.create_user(user_data)

@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(user_data: UserLoginModel, session: AsyncSession = Depends(get_session)):
    _service = UserService(session)
    return await _service.log_user(user_data)

@auth_router.get("/me", status_code=status.HTTP_200_OK, response_model=UserOutModelWithBooks)
async def get_current_user(user: User = Depends(get_current_user)):
    return user

@auth_router.get("/all", status_code=status.HTTP_200_OK, response_model=List[UserOutModelWithBooks], dependencies=[admin_role_checker, access_token_bearer])
async def get_all_users(session: AsyncSession = Depends(get_session), search: str ="", limit: int = 10, offset: int = 0):
    _service = UserService(session)
    return await _service.get_all_users(search, limit, offset)

@auth_router.get("/profile/{user_id}", status_code=status.HTTP_200_OK, response_model=UserOutModelWithBooks)
async def get_user_profile(user_id: int, session: AsyncSession = Depends(get_session)):
    _service = UserService(session)
    return await _service.get_user_by_id(user_id)

@auth_router.patch("/profile/{user_id}", status_code=status.HTTP_200_OK, response_model=UserOutModel)
async def update_user_profile(user_id: int, user_data: UserUpdateModel, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    _service = UserService(session)
    return await _service.update_user_profile(user_id, user_data, current_user)

@auth_router.patch("/profile/{user_id}/role_attribution", status_code=status.HTTP_200_OK, response_model=UserOutModel, dependencies=[ access_token_bearer, admin_role_checker])
async def update_user_role(
    user_id: int,
    role: UserUpdateRoleModel,
    session: AsyncSession = Depends(get_session)
):
    _service = UserService(session)
    return await _service.update_user_role(user_id, role)

@auth_router.patch("/{user_id}/books/{book_id}", status_code=status.HTTP_200_OK, response_model=UserOutModelWithBooks, dependencies=[access_token_bearer])
async def update_user_book(user_id: int, book_id:int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    _service = UserService(session)
    return await _service.update_user_book(user_id, book_id, current_user)