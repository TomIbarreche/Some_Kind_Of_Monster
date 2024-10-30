import datetime, pika, time
import json
from typing import List
from fastapi.responses import JSONResponse
from fastapi import status, BackgroundTasks
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.repository import UserRepository
from src.auth.schemas import NewCreatedUserModel, PasswordResetConfirm, PasswordResetRequest, UserCreationModel, UserLoginModel, UserOutModel, UserOutModelWithBooks, UserUpdateModel
from src.books.service import BookService
from src.errors import UpdateNotAllowed, UserAlreadyExists, UserNotFound, InvalidCredentials, UserNotVerified, RoleNotFound, UserVerificationFailed, ResetPasswordDontMatch
from src.db.models import User
from src.auth.utils import Hasher, TokenMaker, UrlSerializer, create_message
from src.enums import Role
from src.config import settings


class UserService:
    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)
        self.book_service = BookService(session)

    async def create_user(self, user_data: UserCreationModel) -> NewCreatedUserModel:
        if not await self.check_if_user_exists(user_data):
            user_data_dict = user_data.model_dump(exclude_none=True)
            new_user = User(**user_data_dict)
            new_user.password_hash = Hasher.hash_password(user_data_dict['password'])
            new_user.role = Role.USER.value
            new_added_user = await self.repository.create_user(new_user)
            create_message(new_added_user.email, settings.verified_mail_subject)
            return new_added_user
    
    async def create_default_admin(self) -> None:
        admin_data_dict = {
            "username": settings.default_admin_username,
            "password":settings.default_admin_password,
            "first_name": settings.default_admin_username,
            "last_name":settings.default_admin_username,
            "email":settings.default_admin_email,
            "is_verified":True,
            "date_of_birth":datetime.date(2020,1,1)
        }
        admin = User(**admin_data_dict)
        admin.password_hash = Hasher.hash_password(admin_data_dict['password'])
        admin.role = Role.ADMIN.value
        await self.repository.create_user(admin)

    async def check_if_admin_exists(self) -> bool:
        return await self.repository.check_if_admin_exists()
    
    async def check_if_user_exists(self, user_data: dict) -> bool:
        user_exists_by_mail, user_exists_by_username = await self.repository.check_if_user_exists(user_data)
        if user_exists_by_mail:
            raise UserAlreadyExists(info={"error": "This email is already registered by an other user", "data":f"Email: {user_data.email}"})
        
        if user_exists_by_username:
            raise UserAlreadyExists(info={"error": "This username is already registered by an other user", "data":f"Username: {user_data.username}"})
        
        return False
        
    async def log_user(self, user_data: UserLoginModel):
        user = await self.repository.get_user_by_email(user_data.email)
        if user is None:
            raise UserNotFound(info={"error": "The user with this email doesnt exists", "data":f"User email: {user_data.email}"})
        
        if not Hasher.verify_password(user_data.password, user.password_hash):
            raise InvalidCredentials(info={"error": "Unable to login user with those credentials"})
        
        access_token = TokenMaker.create_jwt_token(data_to_encrypt={"email": user.email, "user_id":user.id, "user_role":user.role})
        
        if user.is_verified:
            return JSONResponse(
                content={
                    "message":"Login Successfull",
                    "access_token_bearer": access_token,
                    "user": {
                        "id":user.id,
                        "username":user.username,
                        "email":user.email
                    }
                },
                status_code=status.HTTP_200_OK
            )
        else:
            raise UserNotVerified(info={"error": "The user is trying to login but need to verified his email first", "data":f"User: {user.username}. Email to verified: {user.email}"})

    async def get_user_by_email(self, user_email:str) -> UserOutModel:
        user = await self.repository.get_user_by_email(user_email)
        if user is None:
            raise UserNotFound(info={"error": "The user with this email doesnt exists", "data":f"User email: {user_email}"})
        return user
        
    async def get_all_users(self, search: str, limit: int, offset: int) -> List[UserOutModelWithBooks]:
        users = await self.repository.get_all_users(search, limit, offset)
        return users
    
    async def get_user_by_id(self, user_id: int)-> UserOutModelWithBooks:
        user = await self.repository.get_user_by_id(user_id)
        if user is None:
            raise UserNotFound(info={"error": "No user with this id exists", "data":f"User id: {user_id}"})
        
        return user
    
    async def update_user_profile(self, user_id: int, user_data: UserUpdateModel, current_user: User) -> UserOutModel:
        if user_id != current_user.id:
            raise UpdateNotAllowed(info={"error": "You cant update a profile that is not yours"})
        
        user_to_update = await self.get_user_by_id(user_id)
        if user_to_update.email == user_data.email and user_to_update.username == user_data.username:
            user_to_update = await self.repository.update_user(user_to_update, user_data)
        elif user_to_update.email != user_data.email and user_to_update.username == user_data.username:
            if await self.repository.get_user_by_email(user_data.email) is not None:
                raise UserAlreadyExists(info={"error": "This email is already registered by an other user", "data":f"Email: {user_data.email}"})
            else:
                user_to_update = await self.repository.update_user(user_to_update, user_data)
        elif user_to_update.email == user_data.email and user_to_update.username != user_data.username:
            if await self.repository.is_username_already_taken(user_data.username):
                raise UserAlreadyExists(info={"error": "This username is already registered by an other user", "data":f"Username: {user_data.username}"})
            else:
                user_to_update = await self.repository.update_user(user_to_update, user_data)
        else:
            if not await self.check_if_user_exists(user_data):
                user_to_update = await self.repository.update_user(user_to_update, user_data)

        return user_to_update
    
    async def update_user_role(self, user_id: int, user_role) -> UserOutModel:
        available_roles = Role.__to_list__(self)
        if user_role.role not in available_roles:
            raise RoleNotFound(info={"error":"This role doesnt exists", "data":f"Role : {user_role.role}"})
                               
        user_to_update = await self.get_user_by_id(user_id)

        return await self.repository.update_user(user_to_update,{"role": user_role.role})

    async def update_user_book(self, user_id: int, book_id: int, current_user: User) -> UserOutModelWithBooks:
        if user_id != current_user.id:
            raise UpdateNotAllowed(info={"error": "You can only registered/delete book to your own account"})
        
        user_to_update = await self.get_user_by_id(user_id)
        book = await self.book_service.get_book_by_id(book_id)
        if book in user_to_update.books:
           return await self.repository.remove_book_to_user(user_to_update, book)
        else:
            return await self.repository.add_book_to_user(user_to_update, book)

    async def verify_user(self, token: str):
        try:
            token_data = UrlSerializer.decode_url_safe_token(token)
            user_email = token_data.get("email")
        except Exception:
            raise UserVerificationFailed(info={"error": "Can't access user email from token verification"})
            
        if user_email is not None:
            user_to_update = await self.get_user_by_email(user_email)
            
        if user_to_update:
            user_to_update = await self.repository.update_user(user_to_update, {"is_verified":True})

    async def password_reset_request(self, user_email: PasswordResetRequest):
        email = user_email.email
        create_message(email, settings.password_reset_request_mail_subject)

    async def password_reset_confirm(self, token :str, password_data: PasswordResetConfirm):
        try:
            token_data = UrlSerializer.decode_url_safe_token(token)
            user_email = token_data.get("email")
        except:
            raise UserVerificationFailed(info={"error": "Can't access user email from token verification"})
        
        if user_email is not None: 
            user_to_update = await self.get_user_by_email(user_email)

        if password_data.confirm_password != password_data.new_password:
            raise ResetPasswordDontMatch(info="")
        
        password_hash = Hasher.hash_password(password_data.confirm_password)

        user_to_update = await self.repository.update_user(user_to_update, {"password_hash":password_hash})

