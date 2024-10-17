from typing import List
from sqlmodel import select, or_
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.schemas import NewCreatedUserModel, UserCreationModel, UserOutModel, UserUpdateModel
from src.db.models import User
from src.enums import Role
class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, new_user: User) -> NewCreatedUserModel:
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user

    async def check_if_user_exists(self, user_data: UserCreationModel) -> tuple:
        user_exist_by_mail = await self.get_user_by_email(user_data.email)
        statement= select(User).where(User.username == user_data.username)
        result = await self.session.exec(statement)
        user_exist_by_username = result.first()
        return (user_exist_by_mail is not None, user_exist_by_username is not None)
        

    async def is_username_already_taken(self, username: str) -> bool:
        statement= select(User).where(User.username == username)
        result = await self.session.exec(statement)
        return result.first() is not None

    async def check_if_admin_exists(self) -> bool:
        statement = select(User).where(User.role == Role.ADMIN.value)
        result = await self.session.exec(statement)
        return True if result.first() is not None else False
    
    async def get_user_by_email(self, user_email:str) -> UserOutModel:
        statement = select(User).where(User.email == user_email)
        result = await self.session.exec(statement)
        user = result.first()
        return user
    
    async def get_all_users(self, search: str, limit: int, offset: int) -> List[UserOutModel]:
        statement = select(User).where(or_(User.username.like('%' + search + '%'), User.first_name.like('%' + search + '%'),User.last_name.like('%' + search + '%'), User.email.like('%' + search + '%'))).order_by(User.created_at).offset(offset).limit(limit)
        result = await self.session.exec(statement)
        users = result.unique()
        return users
    
    async def get_user_by_id(self, user_id: int) ->UserOutModel:
        statement = select(User).where(User.id == user_id)
        result = await self.session.exec(statement)
        user = result.first()
        return user
    
    async def update_user(self,user_to_update: User, user_data: dict):
        user_data_dict = user_data.model_dump()
        for k,v in user_data_dict.items():
            setattr(user_to_update, k, v)

        await self.session.commit()
        return user_to_update