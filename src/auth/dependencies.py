from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.service import UserService
from src.db import get_session
from .utils import TokenMaker

class TokenAccessBearer(HTTPBearer):
    def __init__(self, auto_error = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        creds = await super().__call__(request)
        token = creds.credentials
        token_data = TokenMaker.decode_jwt_token(token)
        return token_data
    
async def get_current_user(token_details: dict = Depends(TokenAccessBearer()), session: AsyncSession = Depends(get_session)):
    user_email = token_details["email"]
    _user_service = UserService(session)
    current_user = await _user_service.get_user_by_email(user_email=user_email)
    
    return current_user