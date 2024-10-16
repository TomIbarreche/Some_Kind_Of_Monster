from fastapi import APIRouter, Depends,status
from fastapi.security import  OAuth2PasswordBearer
from src.auth.schemas import NewCreatedUserModel, UserCreationModel, UserLoginModel, UserOutModel
from src.auth.service import UserService
from src.db import get_session
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.models import User
from .dependencies import TokenAccessBearer, get_current_user
auth_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
access_token_bearer = TokenAccessBearer()

@auth_router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=NewCreatedUserModel)
async def create_user(user_data: UserCreationModel, session: AsyncSession = Depends(get_session)):
    _service = UserService(session)
    return await _service.create_user(user_data)

@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(user_data: UserLoginModel, session: AsyncSession = Depends(get_session)):
    _service = UserService(session)
    return await _service.log_user(user_data)

@auth_router.get("/me", status_code=status.HTTP_200_OK, response_model=UserOutModel)
async def coin(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return user
    
    
    

