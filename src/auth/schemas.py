from datetime import date
from pydantic import BaseModel, EmailStr, Field

from src.enums import Role

class UserCreationModel(BaseModel):
    username: str = Field(max_length=12, min_length=3)
    password: str = Field(min_length=8)
    first_name: str
    last_name: str
    date_of_birth: date
    email: EmailStr

class NewCreatedUserModel(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    date_of_birth: date
    email: EmailStr
    role: str
    is_verified: bool

    class Config:
        from_attributes = True

class UserLoginModel(BaseModel):
    email: EmailStr
    password: str

class UserOutModel(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    date_of_birth: date
    email: EmailStr
    role: str

class UserUpdateModel(BaseModel):
    username: str = Field(max_length=12, min_length=3)
    first_name: str
    last_name: str
    date_of_birth: date
    email: EmailStr

class UserUpdateRoleModel(BaseModel):
    role: str