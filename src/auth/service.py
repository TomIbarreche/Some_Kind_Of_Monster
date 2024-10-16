import datetime
from fastapi.responses import JSONResponse
from fastapi import status
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.repository import UserRepository
from src.auth.schemas import NewCreatedUserModel, UserCreationModel, UserLoginModel, UserOutModel
from src.errors import UserAlreadyExists, UserNotFound, InvalidCredentials, UserNotVerified
from src.db.models import User
from src.auth.utils import Hasher, TokenMaker
from src.enums import Role
from src.config import settings

class UserService:
    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)

    async def create_user(self, user_data: UserCreationModel) -> NewCreatedUserModel:
        result = await self.repository.check_if_user_exists(user_data)
        if result[0] is not None:
            raise UserAlreadyExists(info={"error": "This email is already registered by an other user", "data":f"Email: {user_data.email}"})
        
        if result[1] is not None:
            raise UserAlreadyExists(info={"error": "This username is already registered by an other user", "data":f"Username: {user_data.username}"})
        
        user_data_dict = user_data.model_dump(exclude_none=True)
        new_user = User(**user_data_dict)
        new_user.password_hash = Hasher.hash_password(user_data_dict['password'])
        new_user.role = Role.USER.value
        
        new_added_user = await self.repository.create_user(new_user)
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
         
    