from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.schemas import NewCreatedUserModel, UserCreationModel
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
        return (user_exist_by_mail, user_exist_by_username)
        
    async def check_if_admin_exists(self) -> bool:
        statement = select(User).where(User.role == Role.ADMIN.value)
        result = await self.session.exec(statement)
        return True if result.first() is not None else False
    
    async def get_user_by_email(self, user_email:str) -> User:
        statement = select(User).where(User.email == user_email)
        result = await self.session.exec(statement)
        user = result.first()
        return user