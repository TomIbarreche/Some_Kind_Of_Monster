from typing import List
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.service import UserService
from src.db import get_db
from src.db.models import User
from .auth.utils import TokenMaker
from src.enums import Role
from src.errors import InsufficientPermission

class TokenAccessBearer(HTTPBearer):
    def __init__(self, auto_error = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        creds = await super().__call__(request)
        token = creds.credentials
        token_data = TokenMaker.decode_jwt_token(token)
        return token_data
    
async def get_current_user(token_details: dict = Depends(TokenAccessBearer()), session: Session = Depends(get_db)):
    user_email = token_details["email"]
    _user_service = UserService(session)
    current_user = await _user_service.get_user_by_email(user_email=user_email)
    return current_user

class RoleChecker:

    def __init__(self, allowed_roles_list: List[Role]) -> None:
        self.allowed_roles_list = allowed_roles_list

    async def __call__(self, current_user: User = Depends(get_current_user)):

        if current_user.role in self.allowed_roles_list:
            return True
    
        raise InsufficientPermission(info={"error":f"Roles {self.allowed_roles_list} are required", "data":f"Role '{current_user.role}' found"})
    