from typing import List
from sqlmodel import Session, select, or_
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.schemas import NewCreatedUserModel, UserCreationModel, UserOutModel, UserOutModelWithBooks
from src.books.schemas import BookModelOut
from src.db.models import User
from src.enums import Role
class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_user(self, new_user: User) -> NewCreatedUserModel:
        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)
        return new_user

    def check_if_user_exists(self, user_data: UserCreationModel) -> tuple:
        user_exist_by_mail = self.get_user_by_email(user_data.email)
        statement= select(User).where(User.username == user_data.username)
        result = self.session.exec(statement)
        user_exist_by_username = result.first()
        return (user_exist_by_mail is not None, user_exist_by_username is not None)
        

    def is_username_already_taken(self, username: str) -> bool:
        statement= select(User).where(User.username == username)
        result = self.session.exec(statement)
        return result.first() is not None

    def check_if_admin_exists(self) -> bool:
        statement = select(User).where(User.role == Role.ADMIN.value)
        result = self.session.exec(statement)
        return True if result.first() is not None else False
    
    def get_user_by_email(self, user_email:str) -> UserOutModel:
        statement = select(User).where(User.email == user_email)
        result = self.session.exec(statement)
        user =  result.first()
        return user
    
    def get_all_users(self, search: str, limit: int, offset: int) -> List[UserOutModel]:
        statement = select(User).where(or_(User.username.like('%' + search + '%'), User.first_name.like('%' + search + '%'),User.last_name.like('%' + search + '%'), User.email.like('%' + search + '%'))).order_by(User.created_at).offset(offset).limit(limit)
        result = self.session.exec(statement)
        users = result.unique()
        return users
    
    def get_user_by_id(self, user_id: int) ->UserOutModel:
        statement = select(User).where(User.id == user_id)
        result = self.session.exec(statement)
        user = result.first()
        return user
    
    def update_user(self,user_to_update: User, user_data: dict):
        for k,v in user_data.items():
            setattr(user_to_update, k, v)

        self.session.commit()
        return user_to_update
    
    def add_book_to_user(self,user_to_update: UserOutModelWithBooks, book_to_add: BookModelOut) -> UserOutModel:
        user_to_update.books.append(book_to_add)
        self.session.commit()
        return user_to_update
    
    def remove_book_to_user(self,user_to_update: UserOutModelWithBooks, book_to_remove: BookModelOut) -> UserOutModel:
        user_to_update.books.remove(book_to_remove)
        self.session.commit()
        return user_to_update