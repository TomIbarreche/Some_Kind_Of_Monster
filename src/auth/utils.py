from datetime import timedelta, datetime
from src.errors import TokenDecodeFail
from passlib.context import CryptContext
import jwt
from src.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Hasher():

    @staticmethod
    def hash_password(password: str):
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(password: str, hashed_password:str) -> bool:
        return pwd_context.verify(password, hashed_password)
    
class TokenMaker():

    @staticmethod
    def create_jwt_token(data_to_encrypt: dict) -> str:
        to_encode = data_to_encrypt.copy()
        to_encode["exp"] = datetime.now() + timedelta(minutes=settings.access_token_expire_minutes)
        token = jwt.encode(payload=to_encode,key=settings.jwt_secret_key,algorithm=settings.jwt_algorithm)
        return token
    
    @staticmethod
    def decode_jwt_token(token: str) -> dict:
        try:
            token_data =jwt.decode(token,settings.jwt_secret_key , settings.jwt_algorithm)
            return token_data
        except Exception as err:
            raise TokenDecodeFail(info=f"{err}")
        